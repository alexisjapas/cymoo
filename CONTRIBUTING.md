# Welcome to cymoo contributing guide
## Code nomenclature
### Naming conventions
```
CamelCase for classes
camelCase for variables
snake_case for functions and methods
```

### Imports
External imports come first; then, separated by a line break, the internal imports; finally, the code is separated from the imports by two line breaks. Please refer to the example below.
```
from random import choices, randint, gauss, uniform
from time import sleep

from moo.Solution import Solution
from .NSA import NSA


class NSGA2(NSA):
...
```
