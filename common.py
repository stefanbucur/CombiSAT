
class CNFFormula:
    """The representation of a SAT formula in conjunctive normal form"""
    def __init__(self, varCount = 0):
        self.clauses = []
        self.varCount = varCount
        
class SolverBenchmarkData:
    def __init__(self, varCount=None, clauseCount=None, sat=None, time=None):
        self.varCount = varCount
        self.clauseCount = clauseCount
        self.sat = sat
        self.time = time
        
class SATSolver:
    """The base class for a generic solver"""
    def __init__(self):
        pass
    
    def solve(self, formula):
        pass
    
    def getBenchmark(self):
        pass
    
    def abort(self):
        pass