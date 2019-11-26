# Iteration 5: Report

## Responsibilities
 - Add branches to the database: Bhavin, Nico
 - Render tree on the client-side by requesting pre-rendered tiles from the app
 - Buy a Tree Branch: Ted, Bhavin, Nico
Implement the basics of a buy and sell the system for users. By the end of this iteration, the plan is to have some system for tracking the ownership of a branch.
- Write a Message on Tree Branch: Nico, Bhavin, Ted
After laying the groundwork for tracking the ownership of branches, it allows users to write custom messages on any of the branches they own.

## Completed
Ted worked on adding a navigation bar for the website that allows the user to intuitively move through the site. He also worked on adding unit tests to the buying branches page.
Bhavin worked on creating the system to generate all the tiles of the trees at different zoom levels and adding them to the disk or the database. He created a CLI to render tiles to save the position of the tiles and the branches contained in each tile. Additionally, he generated he worked on generating tests to confirm that the tiles and all of the information that they hold is accurate and being saved in the right place.
Nico worked with Bhavin on generating the tiles at different zoom levels, but he focused on the view inventory and the buying screens. For the view inventory, he also created tests to check if branches owned by a user were being properly displayed. For the buying screen, he worked on displaying the branches that are available for purchase and also on filtering them based on the visibility of the branch and the price. 


## Problems and Struggles
This week things ran a lot smoother because we got together a lot more to develop the application. We met on Saturday, Sunday, and on Monday to develop the site and whenever we encountered a problem point, we were able to quickly figure it out because of the proximity between developers. Our main challenge right now is figuring out how to render the text on the front end of the site. We have the backend figured out and the marketplace is progressing really quickly so the main challenge that lies ahead is using JS to overlay text on the branches based on the information provided in the backend. 

## Plan for Iteration 6
- Finishing all the tests for the backend tile rendering program (Bhavin)
- Polishing the tests that we currently have for the marketplace, specifically, for the buy and sell pages (Ted)
 - Completing the buying page with the ability to search for branches with a specific text and also allowing the user to purchase the branch. (Nico)
- Writing a custom message on the tree branch once it has been bought (Ted, Nico)
- Rendering the tree branches on the front-end with JS (Bhavin)
- Adding branches 


## Plan for Iteration 7
- Ensure that tree rendering on the front-end has low latency and is as responsive as possible
- Make the website accessible and work on creating a more responsive website (Ted, Nico)
- Finish work on  the buy and sell system for branches including periodically adding layers to the branches: Ted, Bhavin, Nico
- Work on making the website look visually attractive.
- Continue making UI improvements, and polishing the website by restructuring the website, fixing any glitches or hiccups, and possibly using CSS/Javascript animations to make the user experience feel smooth. Ted, Nico, Bhavin
- Work on features/user stories that were not completed from the previous iteration.

