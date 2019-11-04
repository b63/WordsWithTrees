## Iteration 2: Report 
### Responsibilities
* Login In: Bhavin, Nico, Ted
	* Work on the basic structure of the login functionality (authentication). By the end of this iteration, we should have a way for the user to login in through the home page.
* Sign Up: Nico, Ted
	* Design database to store user credentials securely, and work on the front end to allow a new user to sign up.
* Display the Tree: Nico, Bhavin
	*  Work on coordinating the creation of tree with the backend so that a new random tree isn't generated every time the home page is reloaded. 

### Completed
We met on Sunday at 5 PM in room E204 and worked on coding and merging the code that we created. What we accompmished was 
creating a signup with tests that validate that the forms are appropriately stored in the database. The signup currently stores a hashed 
version of the password submitted and only allows us to store it if the password and the password confirmation match. Additionally,
the password must be at least 7 characters long and must have one upper case character, one lower case character and one digit. Our test validate that hashed passwords are 
stored in the database and all othe user information. We are also checking that all the correct flashed messages are being correctly displayed in order
to make sure that the user experience flows as smoot as possible. The Login is also currently working, but only needs a few tweaks before we merge it to
the Main.
On the fractal tree side of the development, we were able to make the branches contain characters. The problem that we fixed in this iteration is that we can 
currently zoom in as far as possible without losing quality. On the other hand, when we create the tree with characters as branches
there is a problem with rendering everything in high quality. For that reason, we havent added the character branches to the Main and just added
the updated branch viewing to the Main.
### Struggles
Development was a lot smoother once we decided on a working file structure. The main struggle that we are facing right now 
is creating a system so that whenever a user zooms into a branch, just area visible in the user's window gets rendered. We were 
considering doing something like a modified version of geo-hashing because it could be a solution to quickly rendering a lot of
information quickly depending on a 'zooming' threshold.
On the login and signup side of things...
## Plan for Iteration 3
* Buy a Tree Branch:  Implement the basics of a buy and sell system for users. By the end of this iteration, the plan is to have some system for tracking the ownership of a branch.
* Write a Message on Tree Branch: After laying the groundwork for tracking the ownership of branches, allows users to write custom messages on any of the branches they own.

## Plan for Iteration 4
* Work on making the website look visually attractive, and since it will be unlikely that we will have all the plans for previous Iterations completed, work on finishing those.
* Work on User Interaction: Put finishing touches and polish user interactions. By the end of this iteration, the plan is to have the user interactions with the application smooth and look nice.
