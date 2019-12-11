# Iteration 7: Report

## Responsibilities
- Ensure that tree rendering on the front-end has low latency and is as responsive as possible: Bhavin
- Finish work on  the buy and sell system for branches including periodically adding layers to the branches: Ted, Bhavin, Nico
- Continue making UI improvements, and polishing the website by restructuring the website, fixing any glitches or hiccups, and possibly using CSS/Javascript animations to make the user experience feel smooth: Ted, Nico, Bhavin
- Write a Message on Tree Branch: Nico, Bhavin, Ted
- Bidding System (work on implmenting a bidding system when a new layer of trees spawns: Ted, Nico


## Completed
Ted worked on adding a currency for the Marketplace. Along the way, we realized that we need to implement a notification system to notify users about their status of the transaction. For example, when a user sells a branch (seller), it can take a few days to find a buyer to complete the selling process. Once a buyer is found and the transaction is complete, we need to notify the seller and subsequently add the profit earned to the seller’s account.
Bhavin worked on rendering the text onto the branches when creating the tiles and on the displaying the tiles at various zoom levels in the front end. A rudimentary version of zooming and panning was completed. The tiles are stored in the cache folder which is not pushed to remote so the tiles will not initially be available, but once the tiles are rendered with the “render” command, they will be viewable through the home page. 
Nico worked on polishing the marketplace. He wrote tests and the functionality for the buying and selling systems and also worked on improving the website more responsive. He worked on the navigation bar and made it collapsable for smaller devices and making the content scrollable for smaller screen sizes (this still has to be merged into the master branch).


## Problems and Struggles
We are currently working on a bidding system and one of our struggles is defining what is the scope of our project. We have the option of adding a bidding system and making the application exactly how we envisioned it, but the tradeoff is that we won’t have enough time to go over everything and make sure that the features we already have are spotless. We are leaning on adding the bidding system, but it all depends on how quickly we make progress. Additionally, we also have had some problems with debugging without unit tests. We would like to have more integration tests but we have been struggling with making that work without repeating a lot of the code that we have written every time.

## Lesson Learned
The unit tests we wrote would often fail upon the slightest change which we would then spend upwards of 30 minutes trying to fix. This could have been avoided if we had initially invested the time to write more adaptable tests. For example, ids and the likes in SQL queries were often hard-coded into the tests which doesn’t seem to have been the best practice. Once they were updated not be so inflexible, the tests would reliably pass even if our code base had been significantly changed.


## Plan for Final Week
- Continue making UI improvements (Nico and Ted)
- Make website accessible by adding ARIA attributes (Ted and Nico)
- Finish notification system, bidding system (Nico and Ted)
- Polishing the fractal tree and making sure that we have an example to show in class (Bhavin)
