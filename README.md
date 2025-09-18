This set of functions are designed to provide stable matchings between two equally sized groups. Functions are included to solve the stable marriage with indifference problem, where members can be tied in their rankings. 

The algorithms by Robert W. Irving are implemented (https://www.sciencedirect.com/science/article/pii/0166218X9200179P) which provide three types of solutions:
* Weakly stable solutions - No couple exists where both members strictly prefer each other over their current partner. These solutions can include scenarios where person A strictly prefers person B over their current partner and person B is indifferent between person A and their current partner; this leads to weak stability. A weakly stable solution can always be found.
* Strongly stable solutions - No couple exists where both members strictly prefer each other over their current partner and no couple exists where person A prefers person B over their current partner and person B is indifferent. Strongly stable solutions can not always be found.
* Super stable solutions - No couple exists where both members strictly prefer each other over their current partner and no couple exists where both members are indifferent to each other and their current partners. Again, super stable solutions can not always be found.

More information can be found in the [Wikipedia article](https://en.wikipedia.org/wiki/Stable_marriage_with_indifference#cite_note-2).
