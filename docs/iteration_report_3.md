# Iteration 3: Report

## Responsibilites
Bhavin:
- worked on rendering the tree in python with tkinter and caching it for later use 

Ted:
- work on viewing inventory feature

Nico:
- work on login unit test

## Completed
We completed the login feature (unfinished from the last iteration) which allows users to login and logout of our application.
When logging in, we will check whether or not the password entered matches with the hashed password stored in the database. 
Once a user sucessfully logged in, we will set the *user_id* key for the session to the user's unique id in the database.
After that, when a user visits a page that requires loggin in, we will check whether or not the user's id exists in the session.
If not, the user is redirected to the login page. When the user logs out, the user's session is cleared. We also validated the 
login by registering a user and then checking if the session is active.

Besides, logging in, we also worked on the tree generation and the marketplace. For the marketplace we began working on viewing 
the inventory that they own. We worked on requesting the branches owned by the user from the database and adding them to the view.


## Problems and Struggles
Going into this iteration, we did not have a clear plan on how we were going to tackle the problem of making the scaling of 
the tree and rendering of the text performant enough to be usable. After talking with Mark, we decided to implement this functionality
by rendering the image of the tree at various zoom levels beforehand and saving them to disk. Then when the image of the tree
at various zoom levels is needed, the brower would ask for those images from the application and use those saved images to quickly 
draw the tree. When a request for the image of a particular section of a tree at a particular zoom level is requested, the plan
is to also send along data about the branches that are visible in the image, then use Javascript to parse the information
and overlay the messages associated with each branch on top of the image. We plan to limit the amount of text that has to be rendered
by limiting the number of branches that are viewable by the zoom level. This helps us avoid the problem of there being too much
stuff to render for the browser.

## Lessons Learned
This week, we learned about the importance of re-evaluating what we are developing. We went head on with tkinter because it
seemed to be promising, but after encountering several hurdles like having to implement matrix transformation
functions from scratch and it not having anti-aliasint, we decided to pivot and are currently working with pyCairo. We found out 
that we can generate vector graphics with Cairo and we do not believe that scaling the tree will be an issue. Moreover, this 
highlighted the importance of having a detailed plan of not only the features we will be developing, but also the value of thinking 
about the tools we would be using during the development process.


## Plan for Iteration 4
 - Buy a Tree Branch: Ted, Bhavin, Nico
Implement the basics of a buy and sell system for users. By the end of this iteration, the plan is to have some system for tracking the ownership of a branch.
- Write a Message on Tree Branch: Nico, Bhavin, Ted
After laying the groundwork for tracking the ownership of branches, allows users to write custom messages on any of the branches they own.
- Signup improvements: Ted
Pre-populating non-password fields after getting invalid password message
- Cairo tree generation: Bhavin, Nico
Work with Cairo to generate different images at predetermined zoom levels
## Plan for Iteration 5
Work on making the website look visually attractive, and since it will be unlikely that we will have all the plans for previous Iterations completed, work on finishing those.
Work on User Interaction: Put finishing touches and polish user interactions. By the end of this iteration, the plan is to have the user interactions with the application smooth and look nice.
## Plan for Iteration 6
Continue making UI improvements, and polishing the website by restructuring the website, fixing any glitches or hiccups, and possibly using CSS/Javascript animations to make the user experience feel smooth since it is unlikely that it will as poslished as we would want it to be with just one week of work.
Work on features/user stories that were not completed from the previous iteration.
