from problemInstances import frankClasses, IsaBaronClasses
from solver import getSolutionInstance

if __name__ == "__main__":
    ecole_de_Frank = frankClasses.frankClassesInstance()
    ecole_Isabelle = IsaBaronClasses.isaBaronClassesInstance()
#    solutionInstance = getSolutionInstance(class1, 1_000_000_000_000, 4, 0.9965)
#    solutionInstance = getSolutionInstance(ecole_de_Frank, 60_000, 15, 0.99765)
    solutionInstance = getSolutionInstance(ecole_Isabelle, 60_000, 15, 0.99765)
    print(solutionInstance.toString())
