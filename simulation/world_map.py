import random
from simulation.direction import Direction
from simulation.location import Location


class Cell(object):
    def __init__(self, location, can_move_to=True, generates_score=False):
        self.location = location
        self.can_move_to = can_move_to
        self.generates_score = generates_score


def generate_map(height, width, obstacle_ratio, scoring_square_ratio):
    grid = [[None for x in xrange(width)] for y in xrange(height)]

    for x in xrange(width):
        for y in xrange(height):
            if random.random() < obstacle_ratio:
                grid[x][y] = Cell(Location(x, y), can_move_to=False)
            elif random.random() < scoring_square_ratio:
                grid[x][y] = Cell(Location(x, y), can_move_to=True, generates_score=True)
            else:
                grid[x][y] = Cell(Location(x, y))

    return WorldMap(grid)


class WorldMap(object):
    def __init__(self, grid):
        self.grid = grid

    @property
    def all_cells(self):
        return [cell for sublist in self.grid for cell in sublist]

    def is_on_map(self, location):
        num_cols = len(self.grid)
        num_rows = len(self.grid[0])
        return (0 <= location.y < num_rows) and (0 <= location.x < num_cols)

    def get_cell(self, location):
        cell = self.grid[location.x][location.y]
        assert cell.location == location, 'location lookup mismatch: arg={}, found={}'.format(location, cell.location)
        return cell

    def update_score_locations(self, num_avatars):
        pass

    def get_spawn_location(self):
        return random.choice(filter(lambda cell: cell.can_move_to and not cell.generates_score, self.all_cells)).location

    # TODO: cope with negative coords (here and possibly in other places)
    def can_move_to(self, target_location):
        return self.is_on_map(target_location) and self.get_cell(target_location).can_move_to

    # TODO: switch to always deal in fixed coord space rather than floating origin
    # FIXME: make this work with list of lists instead of numpy
    # FIXME: make this work with x and y instead of row and col
    def get_world_view_centred_at(self, view_location, distance_to_edge):
        num_grid_rows, num_grid_cols = self.grid.shape
        view_diameter = 2 * distance_to_edge + 1

        view_map_corner = view_location - Direction(distance_to_edge, distance_to_edge)

        # Non-cropped indices
        row_start = view_map_corner.y
        row_exclusive_end = row_start + view_diameter

        col_start = view_map_corner.x
        col_exclusive_end = col_start + view_diameter

        # Cropped indices
        cropped_row_start = max(0, row_start)
        cropped_row_exclusive_end = min(num_grid_rows, row_start + view_diameter)

        cropped_col_start = max(0, col_start)
        cropped_col_exclusive_end = min(num_grid_cols, col_start + view_diameter)

        assert 0 <= cropped_row_start < cropped_row_exclusive_end <= num_grid_rows
        assert 0 <= cropped_col_start < cropped_col_exclusive_end <= num_grid_cols

        # Extract cropped region
        cropped_view_map = self.grid[cropped_row_start:cropped_row_exclusive_end, cropped_col_start:cropped_col_exclusive_end]

        # Pad map
        num_pad_rows_before = cropped_row_start - row_start
        num_pad_rows_after = row_exclusive_end - cropped_row_exclusive_end

        num_pad_cols_before = cropped_col_start - col_start
        num_pad_cols_after = col_exclusive_end - cropped_col_exclusive_end

        # padded_view_map = np.pad(cropped_view_map,
        #                          ((num_pad_rows_before, num_pad_rows_after), (num_pad_cols_before, num_pad_cols_after)),
        #                          mode='constant', constant_values=-1
        #                          )
        #
        # return padded_view_map
