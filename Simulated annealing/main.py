from problemInstances import frankClasses
from solver import getSolutionInstance

if __name__ == "__main__":
    class1 = frankClasses.frankClassesInstance()
#    solutionInstance = getSolutionInstance(class1, 1_000_000_000_000, 4, 0.9965)
    solutionInstance = getSolutionInstance(class1, 60_000, 15, 0.99765)
    print(solutionInstance.toString())