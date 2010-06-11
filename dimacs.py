from common import CNFFormula
from StringIO import StringIO

# The number of assignments per "v" group in the DIMACS output
DIMACS_SOLUTION_WRAP = 10

def parseDIMACSHeader(inputFile):
    crtLine = inputFile.readline()
    
    # Return a None header at EOF
    if len(crtLine) == 0:
        return (None, None)
    
    crtLine = crtLine.strip() # Remove the surrounding whitespace
    
    # Return an empty header for blank lines
    if len(crtLine) == 0:
        return ("", None)
    
    lineTokens = crtLine.split(None, 1)
    assert len(lineTokens) == 2, "Invalid DIMACS header format"
    assert len(lineTokens[0]) == 1, "Invalid DIMACS header format"
    
    return (lineTokens[0], lineTokens[1])

def parseDIMACSFormula(inputFile):
    varCount = 0
    clauseCount = 0
    
    # Parsing the header
     
    while True:
        (hType, hContents) = parseDIMACSHeader(inputFile)
        
        if hType == "c":
            pass # Ignore the comments, for now
        elif hType == "p":
            formatTokens = hContents.split()
            assert len(formatTokens) == 3, "Invalid formula format specifications"
            assert formatTokens[0] == "cnf", "Invalid formula format - cnf is requested"
            
            varCount = int(formatTokens[1])
            clauseCount = int(formatTokens[2])
            
            break
        else:
            #Ignore any additional header, but don't accept EOF
            assert hType is not None, "Invalid formula format" 
    
    # Read up until the end of the file, and parse the contents
    
    clauseText = inputFile.read()
    clauseTokens = clauseText.split()
    clauseData = [int(tok) for tok in clauseTokens]
    
    formula = CNFFormula(varCount)
    
    crtClause = []
    for elem in clauseData:
        if elem == 0:
            assert len(crtClause) > 0, "Only non-empty clauses allowed"
            
            formula.clauses.append(crtClause)
            crtClause = []
        else:
            negate = False
            if elem < 0:
                negate = True
                elem = -elem
            
            assert elem <= varCount, "Gaps in the variable numbering not allowed"
            
            crtClause.append((elem, negate))
            
    assert len(crtClause) == 0, "Unterminated clause encountered"
    assert len(formula.clauses) == clauseCount, "Clause count inconsistency"
    
    return formula

def parseDIMACSSolution(inputFile):
    solution = []
    sat = None # We don't know yet
    
    while True:
        (hType, hContents) = parseDIMACSHeader(inputFile)
        
        if hType == "s":
            if hContents == "UNSATISFIABLE":
                sat = False
            else:
                assert hContents == "SATISFIABLE", "Invalid satisfiability solution"
                sat = True
            
        elif hType == "v":
            dataValues = [int(tok) for tok in hContents.split()]
            
            for x in dataValues:
                if x == 0:
                    pass
                elif x > 0:
                    solution.append((x, False))
                else:
                    solution.append((-x, True))
        elif hType is None:
            break
        
    # At this point the end of the response was reached, and we expect
    # a clear answer
    
    assert sat is not None, "Incomplete answer"
    
    if sat:
        assert len(solution) > 0, "Inconsistent results"
        
    return solution
    

def emitDIMACSFormula(outputFile, formula, comments=None):
    if comments is not None:
        for comment in comments:
            outputFile.write("c %s\n" % comment)
            
    outputFile.write("p cnf %d %d\n" % (formula.varCount, len(formula.clauses)) )
    
    for clause in formula.clauses:
        for lit in clause:
            value = lit[0]
            if lit[1]:
                value = -value
                
            outputFile.write("%d " % value)
        
        outputFile.write("0\n")
        
def emitDIMACSSolution(outputFile, solution):
    if len(solution) == 0:
        outputFile.write("s UNSATISFIABLE\n")
        return
    
    outputFile.write("s SATISFIABLE\n")
    
    wrapCounter = 0
    
    for elem in solution:
        value = elem[0]
        if elem[1]:
            value = -value
            
        if wrapCounter == 0:
            outputFile.write("v ")
        
        outputFile.write("%d " % value)
        
        wrapCounter = (wrapCounter + 1) % DIMACS_SOLUTION_WRAP
        
        if wrapCounter == 0:
            outputFile.write("\n")
            
    if wrapCounter == 0:
        outputFile.write("v ")
    
    outputFile.write("0\n")
        
def getDIMACSFormula(formula, comments=None):
    strFile = StringIO()
    emitDIMACSFormula(strFile, formula, comments)
    dimacsFormula = strFile.getvalue()
    strFile.close()
    
    return dimacsFormula