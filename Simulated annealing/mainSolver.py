from problemInstances import frankClasses, IsaBaronClasses
from solver.solver import getSolutionInstance

if __name__ == "__main__":
    ecole_de_Frank = frankClasses.frankClassesInstance()
    ecole_Isabelle = IsaBaronClasses.isaBaronClassesInstance()
    # solutionInstance = getSolutionInstance(ecole_de_Frank, 1_000_000, 4, 0.99765)
    solutionInstance = getSolutionInstance(ecole_de_Frank, 300_000, 4, 0.99765)
    print(solutionInstance.toString())