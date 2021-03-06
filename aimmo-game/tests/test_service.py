from unittest import TestCase

import service
from simulation.avatar.avatar_manager import AvatarManager
from .test_simulation.maps import MockPickup, MockCell
from .test_simulation.dummy_avatar import MoveEastDummy
from simulation.location import Location
from simulation.game_state_provider import GameStateProvider
from simulation.game_state import GameState
from simulation.world_map import WorldMap


class TestService(TestCase):

    class DummyAvatarManager(AvatarManager):
        avatars = [MoveEastDummy(1, Location(0, -1))]

    def setUp(self):
        """
        Sets up the JSON of the world state generated by the service file for testing.
        """
        self.avatar_manager = self.DummyAvatarManager()

        CELLS = [
            [
                {'pickup': MockPickup('b'), 'avatar': self.avatar_manager.avatars[0]},
                {},
                {'generates_score': True},
            ],
            [
                {},
                {'habitable': False},
                {'pickup': MockPickup('a')},
            ],
        ]

        grid = {Location(x, y-1): MockCell(Location(x, y-1), **CELLS[x][y])
                for y in range(3) for x in range(2)}

        test_state_provider = GameStateProvider()
        test_state_provider.set_world(GameState(WorldMap(grid, {}), self.avatar_manager))

        self.world_state_json = service.get_game_state(test_state_provider)

    def test_healthy_flask(self):
        """
        Tests the flask service. HEALTHY is returned if the app can be routed to root.
        """
        service.app.config['TESTING'] = True
        self.app = service.app.test_client()
        response = self.app.get('/game-1')
        self.assertEqual(response.data, 'HEALTHY')

    def test_correct_json_player_dictionary(self):
        """
        Ensures the "players" element of the get_game_state() JSON returns the correct information for the dummy
        avatar provided into the world.

        NOTE: Orientation (and others) may be hard coded. This test WILL and SHOULD fail if the functionality is added.
        """
        player_list = self.world_state_json['players']
        self.assertEqual(len(player_list), 1)
        details = player_list[0]
        self.assertEqual(details['id'], 1)
        self.assertEqual(details['location']['x'], 0)
        self.assertEqual(details['location']['y'], -1)
        self.assertEqual(details['health'], 5)
        self.assertEqual(details['orientation'], "north")
        self.assertEqual(details['score'], 0)

    def test_correct_json_score_locations(self):
        """
        Ensures the correct score location in the "score_locations" element; is returned by the JSON.
        """
        score_list = self.world_state_json['scoreLocations']
        self.assertEqual(score_list[0]['location']['x'], 0)
        self.assertEqual(score_list[0]['location']['y'], 1)

    def test_correct_json_north_east_corner(self):
        """
        Top right corner of the map must be correct to determine the map size.
        """
        north_east_corner = self.world_state_json['northEastCorner']
        self.assertEqual(north_east_corner['x'], 1)
        self.assertEqual(north_east_corner['y'], 1)

    def test_correct_json_south_west_corner(self):
        """
        Bottom left corner of the map must be correct to determine the map size.
        """
        south_west_corner = self.world_state_json['southWestCorner']
        self.assertEqual(south_west_corner['x'], 0)
        self.assertEqual(south_west_corner['y'], -1)

    def test_correct_json_era(self):
        """
        Ensure that the era (for the assets in Unity) is correct.

        NOTE: This is hard coded right now to "less_flat". This test should fail when this functionality is added.
        """
        era = self.world_state_json['era']
        self.assertEqual(era, "less_flat")

    def test_correct_json_world_pickups_returned_is_correct_amount(self):
        """
        The JSON returns the correct amount of pickups.
        """
        pickup_list = self.world_state_json['pickups']
        self.assertEqual(len(pickup_list), 2)

    def test_correct_json_world_obstacles(self):
        """
        JSON generated must return correct location, width, height, type and orientation about obstacles.

        NOTE: Obstacles are highly hard coded right now. Only location changes. If any functionality is added, this test
              WILL and SHOULD fail.
        """
        obstacle_list = self.world_state_json['obstacles']
        self.assertEqual(len(obstacle_list), 1)
        self.assertEqual(obstacle_list[0]['location']['x'], 1)
        self.assertEqual(obstacle_list[0]['location']['y'], 0)
        self.assertEqual(obstacle_list[0]['orientation'], "north")
        self.assertEqual(obstacle_list[0]['width'], 1)
        self.assertEqual(obstacle_list[0]['height'], 1)
        self.assertEqual(obstacle_list[0]['type'], "wall")
