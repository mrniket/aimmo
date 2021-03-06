import logging
import time
from threading import Thread

from simulation.action import PRIORITIES

LOGGER = logging.getLogger(__name__)

TURN_INTERVAL = 2


class TurnManager(Thread):
    """
    Game loop
    """
    daemon = True

    def __init__(self, game_state, end_turn_callback, communicator,
                 state_provider, logs_provider):

        self.state_provider = state_provider
        self.logs_provider = logs_provider
        self.state_provider.set_world(game_state)
        self.end_turn_callback = end_turn_callback
        self.communicator = communicator
        super(TurnManager, self).__init__()

    def run_turn(self):
        raise NotImplementedError("Abstract method.")

    def _run_turn_for_avatar(self, avatar):
        """
        Send an avatar its view of the game state and register its
        chosen action & logs.
        """
        with self.state_provider as game_state:
            state_view = game_state.get_state_for(avatar)

        worker_data = avatar.fetch_data(state_view)

        self._register_actions(avatar, worker_data)
        self._register_logs(avatar, worker_data)

    def _register_actions(self, avatar, worker_data):
        """
        Calls a function that constructs the action object, does error handling,
        and finally registers it onto the avatar.

        :param avatar: Avatar object to which logs will be saved.
        :param worker_data: Dict containing (among others) the 'action' key.
        """
        if avatar.decide_action(worker_data):
            with self.state_provider as game_state:
                avatar.action.register(game_state.world_map)

    def _register_logs(self, avatar, worker_data):
        """
        Gathers the logs from the data received. It handles error catching.

        :param avatar: Avatar object to which logs will be saved.
        :param worker_data: Dict containing (among others) the 'log' key.
        """
        try:
            self.logs_provider.set_user_logs(user_id=avatar.player_id,
                                             logs=worker_data['log'])
        except KeyError:
            LOGGER.error("Logs not found in worker_data when registering!")

    def _update_environment(self, game_state):
        num_avatars = len(game_state.avatar_manager.active_avatars)
        game_state.world_map.reconstruct_interactive_state(num_avatars)

    def _mark_complete(self):
        from service import get_world_state
        self.communicator.mark_game_complete(data=get_world_state())

    def _run_single_turn(self):
        self.run_turn()

        with self.state_provider as game_state:
            game_state.update_environment()

        self.end_turn_callback()

        self.logs_provider.clear_logs()

    def run(self):
        while True:
            try:
                self._run_single_turn()
            except Exception:
                LOGGER.exception('Error while running turn')
            with self.state_provider as game_state:
                if game_state.is_complete():
                    LOGGER.info('Game complete')
                    self._mark_complete()
            time.sleep(TURN_INTERVAL)


class SequentialTurnManager(TurnManager):
    def run_turn(self):
        """
        Get and apply each avatar's action in turn.
        """
        with self.state_provider as game_state:
            avatars = game_state.avatar_manager.active_avatars

        for avatar in avatars:
            self._run_turn_for_avatar(avatar)
            with self.state_provider as game_state:
                location_to_clear = avatar.action.target_location
                avatar.action.process(game_state.world_map)
                game_state.world_map.clear_cell_actions(location_to_clear)


class ConcurrentTurnManager(TurnManager):
    def run_turn(self):
        """
        Concurrently get the intended actions from all avatars and regioster
        them on the world map. Then apply actions in order of priority.
        """
        with self.state_provider as game_state:
            avatars = game_state.avatar_manager.active_avatars

        threads = [Thread(target=self._run_turn_for_avatar,
                          args=(avatar,)) for avatar in avatars]

        [thread.start() for thread in threads]
        [thread.join() for thread in threads]

        # Waits applied first, then attacks, then moves.
        avatars.sort(key=lambda a: PRIORITIES[type(a.action)])

        locations_to_clear = {a.action.target_location for a in avatars
                              if a.action is not None}

        for action in (a.action for a in avatars if a.action is not None):
            with self.state_provider as game_state:
                action.process(game_state.world_map)

        for location in locations_to_clear:
            with self.state_provider as game_state:
                game_state.world_map.clear_cell_actions(location)
