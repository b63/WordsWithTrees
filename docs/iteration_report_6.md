# Iteration 6: Report

## Responsibilities
- Finishing all the tests for the backend tile rendering program (Bhavin)
- Polishing the tests that we currently have for the marketplace, specifically, for the buy and sell pages (Ted)
- Completing the buying page with the ability to search for branches with a specific text and also allowing the user to purchase the branch. (Nico)
- Writing a custom message on the tree branch once it has been bought (Ted, Nico)
- Rendering the tree branches on the front-end with JS (Bhavin)
- Adding branches 


## Completed
Ted worked on implementing the feature to enable a user to sell a tree branch and the unit test for this feature. Bhavin finished writing more comphrehensive tests for the backend tile rendering program, including checks to make sure that only the  branches that are actually visible in a tile are being reported as being visible in the output JSON file. He also finished writing the API for requestion tiles/zoom information from the application that will be used by the client-side code to draw the tree. Progress was made in the using the tile to render the tree in the front end, but it is not in working condition yet, so it's not yet commited to master.  


## Problems and Struggles
Although it was Thanksgiving, our team members were still able to work on the project individually. By this time, we have already gotten used to the workflow of writing unit tests, developing feature within a branch, and merging completed working code into master.


## Plan for Final Week
- Ensure that tree rendering on the front-end has low latency and is as responsive as possible: Bhavin
- Finish work on  the buy and sell system for branches including periodically adding layers to the branches: Ted, Bhavin, Nico
- Continue making UI improvements, and polishing the website by restructuring the website, fixing any glitches or hiccups, and possibly using CSS/Javascript animations to make the user experience feel smooth: Ted, Nico, Bhavin
- Write a Message on Tree Branch: Nico, Bhavin, Ted
- Bidding System (work on implmenting a bidding system when a new layer of trees spawns: Ted, Nico
