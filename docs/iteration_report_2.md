## Iteration 2: Report 
### Responsibilities
* Login In: Bhavin, Nico, Ted
	* Work on the basic structure of the login functionality (authentication). By the end of this iteration, we should have a way for the user to login in through the home page.
* Sign Up: Nico, Ted
	* Design database to store user credentials securely, and work on the front end to allow a new user to sign up.
* Display the Tree: Nico, Bhavin
	*  Work on coordinating the creation of tree with the backend so that a new random tree isn't generated every time the home page is reloaded. 

### Completed
We met on Sunday at 5 PM in room E204 and worked on coding and merging the code that we created. What we accomplished was 
creating a signup with tests that validate that the forms are appropriately stored in the database. The signup currently stores a hashed 
version of the password submitted and only allows us to store it if the password and the password confirmation match. Additionally,
the password must be at least 7 characters long and must have one upper case character, one lower case character and one digit. Our test validate that hashed passwords are stored in the database and all othe user information. We are also checking that all the correct flashed messages are being correctly displayed in order to make sure that the user experience flows as smoot as possible.

On the fractal tree side of the development, we were able to make the branches contain characters and make the rendering/generation of the tree much smoother by doing so intermittently. Previously, each layer of the tree would be asynchronously generated, but all the branches in the layer would all be generated in one function call. This would work fine if there were only a few (in the 100's) branches in each layer, but once the number of branches in each layer started hitting the thousands, too much processing time would be hogged and the page would start to become unresponsive. Now, with the use of the Promise API that Javascript proivdes, only 100 or so branches are generated before a timing out for about 100ms so that the page never become unresponsive. The problem that we fixed in this iteration is that we can currently zoom in as far as possible without losing quality. On the other hand, when we create the tree with characters as branches there is a problem with rendering everything in high quality. For that reason, we haven't added the character branches to the main. We weren't able to work on coordinating the creation of tree with the backend so that a new random tree isn't generated every time the home page is reloaded, but that will be one of the main goals for the next iteration. 

### Struggles
Development was a lot smoother once we decided on a working file structure. The main struggle that we are facing right now 
is performance: we need a some way of rendering only a few branches visible on the screen in high quality, while everything else is rendered in low quality. The end product should look something akin to what Google maps has where the details of an area is not loaded until the user zooms and pans to the right place. We were considering doing something like a modified version of geo-hashing because it could be a solution to quickly rendering a lot of information quickly depending on a 'zooming' threshold.

On the login and signup side of things, the backend development went smoothy since we had a guide we could reference when issues cropped up. Although the signup branch has been merged into master, the login branch has not been merged as of the time of writing this report. This is partly due to the fact that the unit test for login has not been done yet. One thing that we need to test is whether or not our application can be logged by multiple users at the same time.

## Important Lessons Learned
By repeatedly having to fetch new changes, resolve merge conflicts and push new changes throughout the development process, we gradually learned to use git more effectively instead of stumbling into a working solution. There were numerous times when we found the `git stash` command really helpful: if a teammate pushed new changes they had been working on while local changes had yet to be finalized for a commit, stashing the local changes then applying them later after pulling the new changes made by the teammate saved a lot of messing about when pushing the local changes later on. We also learned that frequently pulling new changes from the master branch is a good idea, instead of doing a massive merge later on which might involve resolving nasty merge conflicts.   

## Plan for Iteration 3
* Not a random Tree: Nico, Bhavin
	*  Work on coordinating the creation of tree with the backend so that a new random tree isn't generated every time the home page is reloaded.
* Performance Improvements: Nico, Bhavin
	* Figure out a way to do something akin to what is done in Google maps so that only branches that are in the users screen are rendered in high quality as the user pans and zooms.
* Buy a Tree Branch: Ted, Bhavin, Nico 
	* Implement the basics of a buy and sell system for users. By the end of this iteration, the plan is to have some system for tracking the ownership of a branch.
* Write a Message on Tree Branch: Nico, Bhavin, Ted
	* After laying the groundwork for tracking the ownership of branches, allows users to write custom messages on any of the branches they own.

## Plan for Iteration 4
* Work on making the website look visually attractive, and since it will be unlikely that we will have all the plans for previous Iterations completed, work on finishing those.
* Work on User Interaction: Put finishing touches and polish user interactions. By the end of this iteration, the plan is to have the user interactions with the application smooth and look nice.

## Plan for Iteration 5
* Continue making UI improvements, and polishing the website by restructuring the website, fixing any glitches or hiccups, and possibly using CSS/Javascript animations to make the user experience feel smooth since it is unlikely that it will as poslished as we would want it to be with just one week of work.
* Work on features/user stories that were not completed from the previous iteration.
