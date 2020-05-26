from toybox.interventions.base import *
from toybox.interventions.core import * 
try:
  import ujson as json
except:
  import json
import random
from pymonad import Either
from typing import Optional
"""An API for interventions on Amidar."""

# Someday all of these objects will be auto-generated by the Rust. 
# For now, manually specify them.

class Amidar(Game):

  expected_keys = Game.expected_keys + ['enemies', 'player', 'jumps', 'jump_timer', 'chase_timer', 'board']
  immutable_fields = Game.immutable_fields + ['enemies']
  eq_keys = ['score'      ,
             'lives'      ,
             'level'      ,
             'enemies'    ,
             'jumps'      ,
             'jump_timer' ,
             'chase_timer',
             'board'      ,
             'player'     ]
  
  def __init__(self, intervention, 
    score=None, player=None, lives=None, rand=None, level=None,
    enemies=None, jumps=None, jump_timer=None, chase_timer=None, board=None):
    assert intervention
    super().__init__(intervention, score, lives, rand, level)
    assert self.intervention
    self.enemies = EnemyCollection.decode(intervention, enemies, EnemyCollection)
    self.jumps = jumps
    self.jump_timer = jump_timer
    self.chase_timer = chase_timer
    self.board = Board.decode(intervention, board, Board)
    self.player = Player.decode(intervention, player, Player)
    self._in_init = False


class EnemyCollection(Collection):

    expected_keys = []

    def __init__(self, intervention, enemies):
      super().__init__(intervention, enemies, Enemy)
      self._in_init = False

    def decode(intervention, enemies, clz):
      return EnemyCollection(intervention, enemies)

    def make_models(self, data): assert False


class Tile(BaseMixin):
    # Ideally we would have this be an enum, but we'd need to set up 
    # an adaptor class to use multiple inheritence here, and....no.

    Empty = 'Empty'
    Unpainted = 'Unpainted'
    Painted = 'Painted'
    ChaseMarker = 'ChaseMarker'
    tags = [Empty, Unpainted, Painted, ChaseMarker]
    
    expected_keys = []
    eq_keys = ['tag']

    def __init__(self, intervention, name):
      assert intervention
      super().__init__(intervention)
      assert self.intervention
      assert name in Tile.tags, '%s not a valid tile tag' % name      
      self.tag = name
      self._in_init = False

    def decode(intervention, rustname, clz):
      assert type(rustname) == str
      assert intervention
      return Tile(intervention, rustname)

    def encode(self):
      return self.tag

    def make_models(self, data): assert False


class MovementAI(BaseMixin):

    expected_keys = []
    eq_keys = [
      'protocol'           ,       
      'next'               ,
      'default_route_index',
      'start'              ,
      'vert'               ,
      'horiz'              ,
      'start_vert'         ,
      'start_horiz'        ,
      'start_dir'          ,
      'dir'                ,
      'vision_distance'    ,
      'player_seen'        ,
    ]

    EnemyLookupAI     = 'EnemyLookupAI'
    EnemyPerimeterAI  = 'EnemyPerimeterAI' 
    EnemyAmidarMvmt   = 'EnemyAmidarMvmt' 
    EnemyTargetPlayer = 'EnemyTargetPlayer'
    EnemyRandomMvmt   = 'EnemyRandomMvmt'

    mvmt_protocols = [
        EnemyLookupAI, 
        EnemyPerimeterAI, 
        EnemyAmidarMvmt, 
        EnemyTargetPlayer, 
        EnemyRandomMvmt]

    def __init__(self, 
        intervention        : Toybox, 
        protocol            : str,
        next                : Optional[Tile]=None, 
        default_route_index : Optional[int]=None,
        start               : Optional[Tile]=None,
        vert                : Optional[str]=None, 
        horiz               : Optional[str]=None, 
        start_vert          : Optional[str]=None, 
        start_horiz         : Optional[str]=None, 
        start_dir           : Optional[Direction]=None, 
        dir                 : Optional[Direction]=None,
        vision_distance     : Optional[int]=None, 
        player_seen         : Optional[bool]=None):

      super().__init__(intervention)
      assert protocol in MovementAI.mvmt_protocols, '%s not a recognized movement protocol' % protocol
      self.protocol = protocol
      self.next = next
      self.default_route_index = default_route_index
      self.start = start
      self.vert = vert
      self.horiz = horiz
      self.start_vert = start_vert
      self.start_horiz = start_horiz
      self.start_dir = start_dir
      self.dir = dir
      self.vision_distance = vision_distance
      self.player_seen = player_seen
      self._in_init = False

    def decode(intervention, ai, clz):
      ai_name = list(ai.keys())[0]
      ai_kwds = ai[ai_name]
      return MovementAI(intervention, ai_name, **ai_kwds)

    def encode(self):
      args = {}
      for k, v in self.__dict__.items():
        if k not in self.immutable_fields and v is not None and k != 'protocol' :
          args[k] = v.encode() if isinstance(v, BaseMixin) else v
      return { self.protocol: args }

    def make_models(self, data): assert False


class Enemy(BaseMixin):

    expected_keys = ['history', 'step', 'position', 'caught', 'speed', 'ai']
    immutable_fields = BaseMixin.immutable_fields + ['ai']
    eq_keys = expected_keys

    def __init__(self, intervention, history, step, position, caught, speed, ai):
      super().__init__(intervention)
      self.history = history
      self.step = step
      self.position = WorldPoint.decode(intervention, position, WorldPoint)
      self.caught = caught
      self.speed = speed
      self.ai = MovementAI.decode(intervention, ai, MovementAI)
      self._in_init = False

    def make_models(self, data): assert False

class Player(BaseMixin):

    expected_keys = ['history', 'step', 'position', 'caught', 'speed', 'ai']
    eq_keys = expected_keys
    
    def __init__(self, intervention, history, step, position, caught, speed, ai):
        super().__init__(intervention)
        self.history = history
        self.step = step
        self.position = WorldPoint(intervention, **position)
        self.caught = caught
        self.speed = speed
        self.ai = ai
        self._in_init = False

    def decode(intervention, js, clz):
        return Player(intervention, **js)

    def make_models(self, data): assert False


class Board(BaseMixin):

    expected_keys = ['boxes', 'tiles', 'height', 'chase_junctions', 'width', 'junctions']
    immutable_fields = BaseMixin.immutable_fields + ['boxes', 'tiles']
    eq_keys = expected_keys

    def __init__(self, intervention, boxes, tiles, height, chase_junctions, width, junctions):
      assert intervention
      super().__init__(intervention)
      self.width = width
      self.height = height
      self.chase_junctions = chase_junctions
      self.junctions = junctions
      self.boxes = BoxCollection.decode(intervention, boxes,  BoxCollection)
      self.tiles = TileCollection.decode(intervention, tiles, TileCollection)
      self._in_init = False
      
    def make_models(self, data): assert False


class TileCollection(Collection):
    # Convenience class to deal with the fact that the tiles blob is
    # an array of arrays, which messes up how our recursive decode calls

    def __init__(self, intervention, tiles):
      # Instantiate with an empty list, since we are going to want to 
      # make this a list of lists (there should probably be a CollectionCollection
      # in core, since we also have a ColorCollectionCollection there, but I am 
      # not adding this right now EMT 4/17/20)
      assert intervention
      super().__init__(intervention, [], None)
      for row in tiles:
        self.coll.append([Tile.decode(intervention, tile, Tile) for tile in row])
      self._in_init = False

    def remove(self):
      raise ValueError('Cannot remove tiles from the board.')

    def append(self):
      raise ValueError('Cannot add tiles to the board.')

    def pop(self):
      raise ValueError('Cannot remove tiles from the board.')

    def decode(intervention, tiles, clz):
      return TileCollection(intervention, tiles)

    def encode(self):
      return [[t.encode() for t in row] for row in self.coll]


class WorldPoint(BaseMixin):

    expected_keys = ['x', 'y']
    eq_keys = expected_keys
  
    def __init__(self, intervention, x=None, y=None):
      super().__init__(intervention)
      assert type(x) is int
      self.x = x
      self.y = y
      self._in_init = False

    def make_models(self, data): assert False


class BoxCollection(Collection):

    def __init__(self, intervention, boxes):
      super().__init__(intervention, boxes, Box)
      self._in_init = False

    def decode(intervention, boxes, clz):
        return BoxCollection(intervention, boxes)


class Box(BaseMixin):

  expected_keys = ['triggers_chase', 'top_left', 'bottom_right', 'painted']
  eq_keys = expected_keys

  def __init__(self, intervention, triggers_chase, top_left, bottom_right, painted):
      super().__init__(intervention)
      self.triggers_chase = triggers_chase
      self.top_left = TilePoint(intervention, **top_left)
      self.bottom_right = TilePoint(intervention, **bottom_right)
      self.painted = painted
      self._in_init = False

  def make_models(self, data): assert False


class TilePoint(BaseMixin):

    expected_keys = ['tx', 'ty']
    eq_keys = expected_keys

    def __init__(self, intervention, tx, ty):
        super().__init__(intervention)
        self.tx = tx
        self.ty = ty
        self._in_init = False

    def __str__(self):
        return 'TilePoint {tx: %d, ty: %d}' % (self.tx, self.ty)

    def make_models(self, data): assert False


class AmidarIntervention(Intervention):

    # Refactor notes (EMT 12/30/2019)
    # A major change I made to this approach was to define objects for the things we are manipulating. 
    # I figured that that would be easier for a newcomer to get started on, since it would provide 
    # e.g. autocomplete. However, my first pass went too far, I think, since I moved many of @kclary's 
    # interventions to be attached to their associated objects, OOP-style. On second thought, I think
    # that these functions should all pop back up into this object. I believe this will have two major 
    # advantages:
    # (1) We want to be able to auto-genterate these wrappers programmatically, and the more specialized
    #     code that is in them, the harder that becomes
    # (2) We want to be able to automate some experimention, and that will be profoundly easier if we
    #     have a list of interventions with known type signatures that are easily accessible. Attaching
    #     interventions to their associated objects will make searching for them later rather laborious
    #     and therefore error-prone. 

    jump = 'jump'
    chase = 'chase'
    regular = 'regular'
    modes = [jump, chase, regular]

    def __init__(self, tb, game_name='amidar'):
      # check that the simulation in tb matches the game name.
      Intervention.__init__(self, tb, game_name, Amidar)

    def get_random_tile(self, pred=lambda tile: True): 
      """Returns a random tile object, filtered by the input predicate.
      
      Arguments
      ====
      pred:
        boolean function that takes an individual tile as a first argument
        and the rest of the board as the second argument (for making global
        decisions, e.g. only returning the tile if it is some minimum distance
        away from other agents)
      """
      # formerly get_random_tile_id
      while True:
        i = random.randint(0, self.game.board.height - 1)
        j = random.randint(0, self.game.board.width - 1)
        tile = self.game.board.tiles[i][j]
        if pred(tile):
            return tile

    def get_random_track_position(self):
      """Utility function to get a random track tile."""
      # formerly get_random_position
      # grab random tile
      rand_tile = self.get_random_tile(pred=lambda tile: tile.tag != 'Empty')  
      # convert random tile to x,y location 
      return self.tile_to_worldpoint(rand_tile)

    def get_regular_mode(self):
      """Predicate that tells us whether the agent is in 'regular' mode (i.e., not jumping, nor chasing enemies.)"""
      return self.game.jump_timer == 0 and self.game.chase_timer == 0

    def get_jump_mode(self):
      """Predicate indicating whether we are in jump mode, where enemies cannot kill the player."""
      return self.game.jump_timer > 0

    def get_chase_mode(self):
      """Predicate indicating whether we are in chase mode, where the player scores extra points for catching enemies."""
      return self.game.chase_timer > 0

    def any_enemy_caught(self, eid):
      """Predicate indicating whether any enemy has been caught."""
      return any([e.caught for e in self.game.enemies])

    def set_mode(self, mode, set_time=None):
      assert mode in AmidarIntervention.modes
      if mode == AmidarIntervention.jump: 
        self.game.jump_timer = set_time or self.config['jump_time'] 

      elif mode == AmidarIntervention.chase: 
        self.game.chase_timer = set_time or self.config['chase_time'] 

      elif mode == AmidarIntervention.regular:
        self.game.jump_timer = 0
        self.game.chase_timer = 0

      else:
        raise ValueError('set_mode not defined for %s' % mode)

    def set_enemy_protocol(self, enemy, protocol, **kwargs):
      """Sets the enemy movement protocol. Each instance in the rust has a different set of parameters:
  
      EnemyLookupAI
        next: u32
        default_route_index: u32
          
      EnemyPerimeterAI 
        start: TilePoint
  
      EnemyAmidarMvmt 
        vert: Direction
        horiz: Direction
        start_vert: Direction
        start_horiz: Direction
        start: TilePoint 
  
      EnemyRandomMvmt
        start: TilePoint
        start_dir: Direction
        dir: Direction
  
      EnemyTargetPlayer 
        start: TilePoint
        start_dir: Direction
        vision_distance: i32
        dir: Direction
        player_seen: Option<TilePoint>"""
      assert protocol in MovementAI.mvmt_protocols, '%s not a valid protocol' % protocol
      def assert_keys(k, t, option=False): 
        assert k in kwargs, 'Missing argument %s for protocol %s' % (k, protocol)
        v = kwargs[k]
        if option and v is None: return
        t_ = type(v) 
        assert t_ == t, 'Expecting %s to have type %s; is %s' % (k, t, t_)
      if protocol == MovementAI.EnemyLookupAI:
        assert_keys('next', int)
        assert_keys('default_route_index', int)
      elif protocol == MovementAI.EnemyPerimeterAI:
        assert_keys('start', TilePoint)
      elif protocol == MovementAI.EnemyAmidarMvmt:
        assert_keys('vert', Direction)
        assert_keys('horiz', Direction)
        assert_keys('start_vert', Direction)
        assert_keys('start_horiz', Direction)
        assert_keys('start', TilePoint)
      elif protocol == MovementAI.EnemyTargetPlayer:
        assert_keys('start', TilePoint)
        assert_keys('start_dir', Direction)
        assert_keys('vision_distance', int)
        assert_keys('dir', Direction)
        assert_keys('player_seen', TilePoint, option=True)
      elif protocol == MovementAI.EnemyRandomMvmt:
        assert_keys('start', TilePoint)
        assert_keys('start_dir', Direction)
        assert_keys('dir', Direction)
      else: 
        raise ValueError('Unknown enemy movement protocol: %s' % protocol)
      enemy.ai.protocol = protocol
      for k, v in kwargs.items():
        enemy.ai.__setattr__(k, v)

    def is_tile_walkable(self, tile):
      # formerly check_tile_position(self, tdict)
      return tile.tag != Tile.empty

    def set_tile_tag(self, tile, tag):
      assert tag in Tile.tags, 'Unrecognized tile tag: %s' % tag
      tile.tag = tag

    def get_tile_by_pos(self, tx, ty) -> Tile:
      return self.game.board.tiles[ty][tx]

    def filter_tiles(self, pred=lambda t: True):
      lst = []
      for row in self.game.board.tiles:
        for tile in row:
          if pred(tile): lst.append(tile)
      return lst

    def tile_to_tilepoint(self, tile):
      ty, tx = 0, 0
      for y, row in enumerate(self.game.board.tiles):
        for x, t in enumerate(row):
          if t is tile: return TilePoint(self, tx=x, ty=y)
      raise ValueError('Tile %s not found in tiles' % tile)

    def tilepoint_to_worldpoint(self, tp):
      return WorldPoint(self, 
        *self.toybox.query_state_json('tile_to_world', tp.encode()))

    def tile_to_worldpoint(self, tile):
      tp = self.tile_to_tilepoint(tile)
      return self.tilepoint_to_worldpoint(tp)   

    def worldpoint_to_tilepoint(self, wp):
     return TilePoint(self, 
       *self.toybox.query_state_json('world_to_tile', wp.encode()))   

    def set_player_random_start(self, min_enemy_distance=5):
      def within_min_manhattan(t):
        tp = self.tile_to_tilepoint(t)
        for e in self.game.enemies:
          etp = self.worldpoint_to_tilepoint(e.position)
          delta_x = abs(etp.tx - tp.tx)
          delta_y = abs(etp.ty - tp.ty)
          if delta_x + delta_y < min_enemy_distance:
            return False
        return True
          
      pos = self.get_random_tile(pred=within_min_manhattan)
      self.game.player.position = self.tile_to_worldpoint(pos)

    def get_random_dir_for_tile(self, tiles):
        assert tile.tag != "Empty"
        selected = False
        dirs = ["Up", "Down", "Left", "Right"]

        d = None
        while not selected: 
            next_tid = {}
            next_tid['tx'] = tile.tx
            next_tid['ty'] = tile.ty

            if d is not None: 
                dirs.remove(d)
                if not dirs: 
                    d = None

            d = random.choice(dirs)
            if d == "Up":
                next_tid['ty'] = next_tid['ty'] - 1
            elif d == "Down": 
                next_tid['ty'] = next_tid['ty'] + 1
            elif d == "Left": 
                next_tid['tx'] = next_tid['tx'] - 1
            elif d == "Right":
                next_tid['tx'] = next_tid['tx'] + 1

            if d is not None: 
                selected = not selected and self.is_tile_walkable(Tile.decode(self, next_tid, Tile))

        if d is None:
            raise Exception("No valid direction from this tile:\t\tTile tx:"+str(tid['tx'])+", ty"+str(tid['ty']))
        return d




### difficult interventions ###
    # random start state?
    # enemy perimeter direction 
    # tie random selections to Toybox environment seed?


if __name__ == "__main__":
  with Toybox('amidar') as tb:

    # This should all be moved to a testing framework

    # random track position
    with AmidarIntervention(tb) as intervention:
      pos = intervention.get_random_track_position()

    # player random start
    with AmidarIntervention(tb) as intervention:
      intervention.set_player_random_start()
    
    # test painting
    with AmidarIntervention(tb) as intervention:
      tile = intervention.get_tile_by_pos(tx=0, ty=0)
      assert tile.intervention
      intervention.set_tile_tag(tile, Tile.Painted)
      assert intervention.dirty_state

    with AmidarIntervention(tb) as intervention:
      assert intervention.get_tile_by_pos(0, 0).tag == Tile.Painted
      assert not intervention.dirty_state


    # test unpainting
    with AmidarIntervention(tb) as intervention:
      tile = intervention.get_tile_by_pos(0, 0)
      intervention.set_tile_tag(tile, Tile.ChaseMarker)
      assert intervention.dirty_state
    
    with AmidarIntervention(tb) as intervention:
      assert intervention.get_tile_by_pos(0, 0).tag == Tile.ChaseMarker
      assert not intervention.dirty_state


    # get number of enemies
    with AmidarIntervention(tb) as intervention: 
      assert len(intervention.game.enemies) == 5
      assert not intervention.dirty_state

    # remove enemy
    with AmidarIntervention(tb) as intervention:
      enemies = intervention.game.enemies
      enemies.remove(enemies[4])
      assert len(enemies) == len(intervention.game.enemies)
      assert intervention.dirty_state
    # check number of enemies
    with AmidarIntervention(tb) as intervention: 
      assert len(intervention.game.enemies) == 4
      assert not intervention.dirty_state


    # add enemy with 'EnemyLookupAI' protocol
    with AmidarIntervention(tb) as intervention: 
      enemies = intervention.game.enemies
      # copy the second enemy
      enemy = Enemy.decode(intervention, enemies[1].encode(), Enemy)
      next = max([e.ai.next for e in enemies]) + 1
      # Not sure what default route index refers to, so I am picking an arbitrary number
      default_route_index = 10
      intervention.set_enemy_protocol(enemy, MovementAI.EnemyLookupAI, 
        next=next, default_route_index=default_route_index) 
      enemies.append(enemy)
      assert intervention.dirty_state

    with AmidarIntervention(tb) as intervention: 
      assert len(intervention.game.enemies) == 5
      assert not intervention.dirty_state

    # change to 'EnemyPerimeterAI' protocol
    with AmidarIntervention(tb) as intervention: 
      enemy = intervention.game.enemies[-1]
      intervention.set_enemy_protocol(enemy, MovementAI.EnemyPerimeterAI,
        start=TilePoint(intervention, tx=0, ty=0))
      assert intervention.dirty_state
    with AmidarIntervention(tb) as intervention: 
      assert intervention.game.enemies[-1].ai.protocol == MovementAI.EnemyPerimeterAI
      assert not intervention.dirty_state

    # change to 'EnemyAmidarMvmt' protocol
    with AmidarIntervention(tb) as intervention: 
      enemy = intervention.game.enemies[-1]
      intervention.set_enemy_protocol(enemy, 'EnemyAmidarMvmt',
        vert=Direction(intervention, random.choice(Direction.directions)),
        horiz=Direction(intervention, random.choice(Direction.directions)),
        start_vert=Direction(intervention, random.choice(Direction.directions)),
        start_horiz=Direction(intervention, random.choice(Direction.directions)),
        start=TilePoint.decode(intervention, enemy.ai.start, TilePoint)
        )
      assert intervention.dirty_state
    with AmidarIntervention(tb) as intervention: 
      assert intervention.game.enemies[-1].ai.protocol == MovementAI.EnemyAmidarMvmt
      assert not intervention.dirty_state

    # change to 'EnemyTargetPlayer' protocol
    with AmidarIntervention(tb) as intervention: 
      enemy = intervention.game.enemies[-1]
      intervention.set_enemy_protocol(enemy, 'EnemyTargetPlayer',
        start=TilePoint.decode(intervention, enemy.ai.start, TilePoint),
        vision_distance=10,
        player_seen=None,
        start_dir=Direction(intervention, random.choice(Direction.directions)),
        dir=Direction(intervention, random.choice(Direction.directions))
      )
      assert intervention.dirty_state
    with AmidarIntervention(tb) as intervention: 
      assert intervention.game.enemies[-1].ai.protocol == MovementAI.EnemyTargetPlayer
      assert not intervention.dirty_state

    # change to 'EnemyRandomAI' protocol
    with AmidarIntervention(tb) as intervention: 
      enemy = intervention.game.enemies[-1]
      intervention.set_enemy_protocol(enemy, 'EnemyRandomMvmt',
        start=TilePoint.decode(intervention, enemy.ai.start, TilePoint),
        start_dir=Direction(intervention, random.choice(Direction.directions)),
        dir=Direction(intervention, random.choice(Direction.directions)),
      )
      assert intervention.dirty_state
    with AmidarIntervention(tb) as intervention: 
      assert intervention.game.enemies[-1].ai.protocol == MovementAI.EnemyRandomMvmt
      assert not intervention.dirty_state

    # check number of jumps
    with AmidarIntervention(tb) as intervention: 
      assert intervention.game.jumps == 4
      intervention.game.jumps = 5
      assert intervention.dirty_state
    with AmidarIntervention(tb) as intervention:            
      assert intervention.game.jumps == 5
      assert not intervention.dirty_state
 
    # check jump mode
    with AmidarIntervention(tb) as intervention:
      intervention.set_mode('jump')
      assert intervention.dirty_state
    with AmidarIntervention(tb) as intervention:
      assert intervention.game.jump_timer > 0 
      assert not intervention.dirty_state

    # check random starts
    with AmidarIntervention(tb) as intervention:
      initial_start = intervention.game.player.position
      assert not intervention.dirty_state
    with AmidarIntervention(tb) as intervention:
      intervention.set_player_random_start()
      assert intervention.dirty_state
      wp = intervention.game.player.position
      assert wp.x != initial_start.x or wp.y != initial_start.y

    with AmidarIntervention(tb) as intervention:
        try:
            intervention.game.player.intervention = None
            assert False, 'We should not be able to manually set the toybox object after initialization'
        except: pass

        try:
            intervention.game.player._in_init = True
            assert False, 'We should not be able to manulaly set the _in_init flag'
        except: pass

        assert '_in_init' in intervention.game.player.immutable_fields