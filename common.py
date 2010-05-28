
class CNFFormula:
    """The representation of a SAT formula in conjunctive normal form"""
    def __init__(self, varCount = 0):
        self.clauses = []
        self.varCount = varCount
        
class SATSolver:
    """The base class for a generic solver"""
    def __init__(self):
        pass
    
    def solve(self, formula):
        pass
    
    def abort(self):
        pass