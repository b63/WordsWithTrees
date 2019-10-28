## Iteration 1: Report 

### Responsibilities:
Bhavin
* Create the template for the homepage with fillers for different sections of the homepage

Nico, Ted
 -  design database system to keep track of user's inventory
 -   output branches owned by user
 -  design database system to keep track of branches available for purchase and prices
 -   output branches available for purchase and prices

### Completed
We met on Saturday at 3PM in room E204 and talked about the overall architecture of the application.  The directory structure of our project was also discussed during the meeting, the skeleton of which can be found in by navigating to `/docs/architecture.md` of the github repository.

For the client side of the application, we decided that recruiting the help of a third party Javascript library for 2D graphics would be useful, and settled on a library called `Easel.js`.  We found that the use of the library simplified a lot of problems we thought we were going to have when implementing certain features of our application.

We also came up with a rudimentary design of a database for storing information about the branches. The 'branches' table contains columns such as text, owner_id, price, etc. The table will have a relation with another table called 'users' when we we create the sign up and login pages.


## Plan for Iteration 2
* Login In: Bhavin, Nico, Ted
	* Work on the basic structure of the login functionality (authentication). By the end of this iteration, we should have a way for the user to login in through the home page.
* Sign Up: Nico, Ted
	* Design database to store user credentials securely, and work on the front end to allow a new user to sign up.
* Display the Tree: Nico, Bhavin
	*  Work on coordinating the creation of tree with the backend so that a new random tree isn't generated every time the home page is reloaded. 

## Plan for Iteration 3
* Buy a Tree Branch:  Implement the basics of a buy and sell system for users. By the end of this iteration, the plan is to have some system for tracking the ownership of a branch.
* Write a Message on Tree Branch: After laying the groundwork for tracking the ownership of branches, allows users to write custom messages on any of the branches they own.

## Plan for Iteration 4
* Work on making the website look visually attractive, and since it will be unlikely that we will have all the plans for previous Iterations completed, work on finishing those.
* Work on User Interaction: Put finishing touches and polish user interactions. By the end of this iteration, the plan is to have the user interactions with the application smooth and look nice.