from builtins import next
from SCons.Script import *
import os
import re

try:
  from traj import MeasurementsTable
except ImportError:
  def MeasurementsTable(x):
    raise Exception("No module named traj")

try:
  from ui.genetiff import Reader
  def thumbnail(target, source, env):
    import Image
    Image.fromarray( Reader(source[0].path)[0] ).save( target[0].path )
except ImportError:
  def thumbnail(target,source,env):
    raise Exception("No module named ui.genetiff")

def change_label( name, newlabel ):
  if name.rfind(']')==-1:
    pfx,ext = os.path.splitext(name)
    return'%s[%s]%s'%(pfx,newlabel,ext)
  else:
    return re.sub( '(?<=\[).*(?=\]($|\.))',newlabel, name ) #substitutes the last label before the dot

def change_ext( node, newext ):
  prefix,ext = os.path.splitext( node.path )
  target = env.File( os.path.split(prefix)[1] + newext )
  return target


def length_v_score_plot(target,source,env):
  import matplotlib
  matplotlib.use('Agg')
  from pylab import plot, savefig, figure, close
  data = MeasurementsTable( source[0].path ).get_shape_table()
  f = figure()
  plot(data[:,0],data[:,1],'k.',markersize=1, hold=0)
  savefig( target[0].path )
  close(f)

def dfs_consume_tuples(g,cur):
  while isinstance(cur,tuple):
    yield cur
    cur = next(g)
  def rest():
    yield cur
    for e in g:
      yield e
  yield rest()

def flatten(tree):
  isbranch = lambda y: any( [isinstance(y,x) for x in [tuple,
                                 list,
                                 SCons.Node.NodeList]])
  if not isbranch(tree):
    yield tree
  else:
    for node in tree:
      if isbranch(node):
        for e in flatten(node):
          yield e
      else:
        yield node

def dfs_reduce(f,tree):
  """
  >>> a = (0,1,2,(3,4,(5,),(6,)),(7,8),9,0,1,2,(4,(5,),6),7)
  >>> f = lambda x,y: str(x)+str(y)
  >>> list(dfs_reduce(f,a))
  ['012345', '012346', '01278', '012901245', '012901246', '01290127']
  """
  def _dfs_reduce(f,tree, a = None):
    tree = iter(tree)
    for node in tree:
      if isinstance(node,tuple):
        return tuple ( [_dfs_reduce( f, e, a ) for e in dfs_consume_tuples(tree,node)]
                    )
      else:
        a = node if a is None else f(a,node)                   #process node
    return a
  res =  flatten(_dfs_reduce(f,tree))
  #for e in  map(str,res):
  #  print e
  return res

def pipeline_standard(env, movie):
  def alter(j,subdir,ext):
    return env.File(j).Dir(subdir).File(  os.path.splitext(os.path.split(j.path)[-1])[0]+ext  )

  builders = [
    movie,
    ( env.Bar,
      (env.Precious,),
    ),
    env.Whisk,
    (env.Precious,),
    env.Measure,
    env.Classify,
    env.HmmLRTimeWatershedSolver,
    env.GreyAreaSolver,
    env.Summary    
  ]

  compose = lambda a,b: b(a)
  jobs = dfs_reduce( compose, builders )
  return jobs

def pipeline_production(env, sources):
  def alter(j,subdir,ext):
    return env.File(j).Dir(subdir).File(  os.path.splitext(os.path.split(j.path)[-1])[0]+ext  ) 

  builders = [ 
    sources,           #start with movie files
    env.Whisk,
    (env.Precious,),
    lambda j: env.Command( change_ext(j[0], '.measurements'), j, 
                          [ "measure --face $FACEHINT $SOURCE $TARGET" ,
                            "classify $TARGET $TARGET $FACEHINT -n $WHISKER_COUNT --px2mm $PX2MM",
                            "reclassify -n $WHISKER_COUNT $TARGET $TARGET"]),
  ]

  compose = lambda a,b: b(a)
  jobs = dfs_reduce( compose, builders )                         
  return jobs

def pipeline_oconnor(env, movie):
  def start(mov):
    b = env.Bar(mov)
    env.Precious(b)
    w = env.Whisk(mov)
    env.Precious(w)
    return env.MeasureWithBar(w+b)
  builders = [
    movie,
    start,
    env.ClassifyNoHairs,
    ( env.MeasurementsAsTrajectories,),
    ( env.MeasurementsAsMatlab,),
    env.Summary
  ]

  compose = lambda a,b: b(a)
  jobs = dfs_reduce( compose, builders )
  return jobs

def pipeline_curated(env, source):
  def commit_traj(node):
    """ expects source to be a curated whiskers file
        generated target is a measurements file
        returns target node
    """
    node = node[0]
    target  = change_ext( node, '[traj].measurements' )
    sources = [change_ext(node, e) for e in ['.measurements',
                                                  '.trajectories']]
    out = env.Command( target, sources, "measure.py $SOURCES $TARGET" )
    return out

  builders = [
    source,
    env.Measure,
    commit_traj,
    env.Summary
  ]
  compose = lambda a,b: b(a)
  jobs = dfs_reduce( compose, builders )
  return jobs

def lit(s):
  return lambda env,sources: s

def whisk_generator( source, target, env, for_signature ):
  if not target[0].exists():
    return Action("trace $SOURCE $TARGET")
  else:
    return Action("")

def bar_generator( source, target, env, for_signature ):
  if not target[0].exists():
    return Action("whisk $SOURCE $TARGET --no-whisk")
  else:
    return Action("")

env  = Environment(
  ENV = {'PATH':os.environ['PATH']},
  PX2MM = 0,
  BUILDERS = {
    'Thumbnail' : Builder(action = thumbnail),
    'LengthVScorePlot': Builder(action = length_v_score_plot),
    'Whisk' : Builder(generator = whisk_generator,
                      suffix  = '.whiskers',
                      src_suffix = '.seq'
                     ),
    'Bar'   : Builder(generator = bar_generator,
                      #action = "whisk $SOURCE $TARGET --no-whisk",
                      suffix  = '.bar',
                      src_suffix = '.seq'
                     ),
    'Heal'  : Builder(action = "test_merge_collisiontable_3 $SOURCE $TARGET",
                      suffix = '.whiskers',
                      src_suffix = '.whiskers'
                     ),
    'Measure': Builder(action = "test_measure_1 --face $FACEHINT $SOURCE $TARGET",
                       suffix     = '.measurements',
                       src_suffix = '.whiskers'
                      ),
    'MeasureWithBar': Builder(action = "test_measure_1 --face $FACEHINT $SOURCES $TARGET",
                        suffix     = '.measurements',
                        src_suffix = '.whiskers'
                        ),
    'MeasureOld': Builder(action = "measure.py $SOURCE $TARGET --face=$FACEHINT",
                       suffix     = '.measurements',
                       src_suffix = '.whiskers'
                      ),
    'MeasurementsAsMatlab': Builder(action = "measure.py $SOURCE $TARGET",
                                    suffix = '.mat',
                                    src_suffix = '.measurements'
                                   ),
    'MeasurementsAsTrajectories': Builder(action = lambda source,target,env: 0 if MeasurementsTable(source[0].path).save_trajectories(target[0].path,excludes=[-1]) else 1,
                                          suffix = '.trajectories',
                                          src_suffix = '.measurements'),
    'Classify': Builder(action = "test_classify_1 $SOURCE $TARGET $FACEHINT -n $WHISKER_COUNT --px2mm $PX2MM --follicle $FOLLICLE_THRESH",
                        suffix = { '.measurements' : "[autotraj].measurements" },
                        src_suffix = ".measurements"
                       ),
    'ClassifyNoHairs': Builder(action = "test_classify_3 $SOURCE $TARGET $FACEHINT -n $WHISKER_COUNT",
                        suffix = { '.measurements' : "[autotraj].measurements" },
                        src_suffix = ".measurements"
                       ),
    'Summary': Builder(action = "summary.py $SOURCE $TARGET --px2mm=$PX2MM",
                       src_suffix = ".measurements",
                       suffix = ".png"),
    'SummaryPDF': Builder(action = "summary.py $SOURCE $TARGET --px2mm=$PX2MM",
                       src_suffix = ".measurements",
                       suffix = ".pdf"),
    'GreyAreaSolver': Builder(action = "test_traj_solve_gray_areas $SOURCE $TARGET",
                              src_suffix = ".measurements",
                              suffix = lit( "[grey_v0].measurements") ),
    'HmmLRSolver': Builder(action = "test_hmm_reclassify_1 -n $WHISKER_COUNT $SOURCE $TARGET",
                              src_suffix = ".measurements",
                              suffix = lit( "[hmm-lr].measurements")),
    'HmmLRDelSolver': Builder(action = "test_hmm_reclassify_2 -n $WHISKER_COUNT $SOURCE $TARGET",
                              src_suffix = ".measurements",
                              suffix = lit( "[hmm-lrdel].measurements")),
    'HmmLRTimeSolver': Builder(action = "test_hmm_reclassify_3 -n $WHISKER_COUNT $SOURCE $TARGET",
                              src_suffix = ".measurements",
                              suffix = lit( "[hmm-lr-time].measurements")),
    'HmmLRTimeWatershedSolver': Builder(action = "test_hmm_reclassify_5 -n $WHISKER_COUNT $SOURCE $TARGET",
                              src_suffix = ".measurements",
                              suffix = lit( "[hmm-watershed].measurements")),
    'HmmLRDelTimeSolver': Builder(action = "test_hmm_reclassify_4 -n $WHISKER_COUNT $SOURCE $TARGET",
                              src_suffix = ".measurements",
                              suffix = lit( "[hmm-lrdel-time].measurements")),
  }
)

#env.Decider('timestamp-newer')
env.AppendENVPath('PATH', os.getcwd())
env['WHISKER_COUNT'] = -1  # a count <1 tries to measure the count for each movie
                           # a count >= 1 will identify that many whiskers in each movie
env['FOLLICLE_THRESH'] = 0 # all the follicle positions fall on one side of this line
                           # whether the line lies in `x` or `y` depends on the
                           # face orientation which is infered

env.AddMethod( pipeline_production, "Pipeline" )
env.AddMethod( pipeline_curated, "CuratedPipeline" )
env.AddMethod( pipeline_oconnor, "OConnorPipeline" )

Export('env')

if __name__=='__main__':
  import doctest
  doctest.testmod()
