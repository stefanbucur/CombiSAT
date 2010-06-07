import shlex
import subprocess
import errno

from threading import Thread
from threading import Semaphore

from common import SATSolver
from common import CNFFormula

from dimacs import getDIMACSFormula
from dimacs import parseDIMACSSolution
from dimacs import emitDIMACSSolution

from StringIO import StringIO
    
class ExternalSolver(SATSolver):
    def __init__(self, path):
        self.path = path
        
        args = shlex.split(self.path)
        self.proc = subprocess.Popen(args,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     close_fds=True)
        
    def solve(self, formula):
        # Compose the formula to send
        dimacsFormula = getDIMACSFormula(formula)
        
        try:
            (outdata, errdata) = self.proc.communicate(dimacsFormula)
        except OSError as error:
            if error.errno == errno.EPIPE:
                pass
            else:
                raise
        
        if self.proc.returncode >= 0 and len(outdata) > 0:
            solFile = StringIO(outdata)
            solution = parseDIMACSSolution(solFile)
            return solution
        
    def abort(self):
        try:
            self.proc.kill()
        except OSError as error:
            if error.errno == errno.ESRCH:
                pass
            else:
                raise
            
class _PortfolioThread(Thread):
    def __init__(self, solver, formula, sem):
        Thread.__init__(self)
        
        self.solution = None
        self.solver = solver
        self.formula = formula
        self.sem = sem
        
    def run(self):
        self.solution = self.solver.solve(self.formula)
        self.sem.release()
    
class PortfolioSolver(SATSolver):
    """A strategy portfolio SAT solver"""
    def __init__(self, solvers):
        self.solvers = solvers
        
    def _solve_mt(self, formula):
        solverThreads = []
        solution = None
        
        sem = Semaphore(0)
        
        for solver in self.solvers:
            sThread = _PortfolioThread(solver, formula, sem)
            solverThreads.append(sThread)
            
            sThread.start()
        
        # Wait for at least one thread to finish
        sem.acquire()
            
        for sThread in solverThreads:
            if solution is None:
                if sThread.solution is not None:
                    solution = sThread.solution
            
            sThread.solver.abort()
                
        assert solution is not None, "Solver returned with invalid solution"
                
        for sThread in solverThreads:
            sThread.join()
            
        return solution
    
    def _solve_st(self, formula):
        assert len(self.solvers) == 1
        solver = self.solvers[0]
        
        solution = solver.solve(formula)
        
        return solution
        
    def solve(self, formula):
        if len(self.solvers) > 1:
            return self._solve_mt(formula)
        else:
            return self._solve_st(formula)
        
    def abort(self):
        pass