**Estimates**: time estimates are based on the number of people involved in developing the feature and the predicted complexity to complete the feature.

**Priority**: Priority is based on feature hierarchy. This means that if a feature is required before other features can be developed, then its priority is high. 

# User Stories

Sign Up
-----------------
As a User, I want to sign up for an account so that I can start buying and selling tree branches.

 - Priority: High
 - Estimate: 1 week
 - Confirmation:
 
    1. “Account successfully created” message pops up
    2. User is redirected to login page
    
    
    
Login
-----------------
As a User, I want to login to my account so that I can view my inventory, buy, and sell tree branches.

 - Priority: High
 - Estimate: 1 week
 - Confirmation:
 
   1. User is redirected to the Marketplace
   2. User’s name appears at right corner of homepage
   
   
   
Write A Message on Tree Branch
-----------------
As a User, I want to write a message on a tree branch bought so that my message shows up on my tree branch in the Marketplace.

 - Priority: High
 - Estimate: 1 week
 - Confirmation:
 
   1. “You’ve successfully write a message on your tree branch” message pops up
   2. Tree branch message box is not empty
   3. User is redirected to Marketplace
   

Buy Tree Branches (Epic)
-----------------
As a User, I want to buy a tree branch so that I can write words on it and add it to my inventory.

 - Priority: Low
 - Estimate: 2 week
 - Confirmation:
 
    1. Click on a branch that can be bought.
    2. User is redirected to a page that shows how much tokens it would cost and who currents owns it.
    3. If the user has enough tokens to buy, then confirming purhcase will change ownership of the branch to the user who bought it.
    4. Confirm that branch is no longer listed as available for purchase.
    5. Confirm that the user's token has decreased by the price of the branch.
    6. User who just bought the branch is prompted for custom text that will be displayed on the branch.
    7. User’s token decreases by the price bought
    8. Confirm that user who owns the branch has more tokens.
    
 
Token Possession
-----------------
As a user, I want to be able to tell how many tokens I have in my possession.

  - Priority: High
  - Estimate: 1 day
  - Confirmation:
  
    1. User accesses any page while logged in.
    2. User can see the number of token in their poessession on the top right corner.


   
Display the Tree
-----------------
As a user, I want to be able to view the tree on the homepage.
 
  - Priority: High
  - Estimate: 1 week
  - Confirmation:
  
    1. User accesses any page.
    2. A tree is displayed on the page with the correct number of layers.



Sell Tree Branches
-----------------
As a User, I want to sell a tree branch for a price and make it available to be bought in the marketplace("the forest").
 - Priority: High
 - Estimate: 1 week
 - Confirmation:
 
   1. User access the homepage and clicks on a branch that they owns.
   2. User clicks on the sell button and is prompted for a starting price.
   


Delete Account
-----------------
As a User, I want to delete my account so that I no longer own any tree branches.

 - Priority: Low
 - Estimate: 1 week
 - Confirmation:
 
   1. “Account successfully deleted” message pops up
   2. User’s information is removed from database
   3. Any tree branches owned by the user become available for sale in the Marketplace with empty text
    
 
 
Marketplace/Homepage (Epic User Story)
-----------------
As a User, I want to buy and sell tree branches at the Marketplace so I can change the number of tree branches that I own and make money.

 - Priority: Low
 - Estimate: 5 weeks
 - Confirmation:
 
    1. User’s total number of tokens will change depending on if they sold or bought a branch
    2. The user’s inventory will be updated depending on what was bought or sold in the marketplace.
    3. The contents of the Marketplace will be updated if the user buys or sells an item.
 
 

