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
   
   

Buy Tree Branches
-----------------
As a User, I want to buy a tree branch so that I can write words on it and add it to my inventory.

 - Priority: High
 - Estimate: 1 week
 - Confirmation:
 
    1. User is redirected to another webpage where he/she can write a message on the tree branch bought
    2. “You just bought a tree branch! Now write on it.” message pops up
    3. User’s token decreases by the price bought
    
    

Sell Tree Branches
-----------------
As a User, I want to sell a tree branch so that I can remove it from my inventory and make the tree branch with empty message available for sale again on the Marketplace.

 - Priority: High
 - Estimate: 1 week
 - Confirmation:
 
   1. “Tree branch successfully removed from your inventory” message pops up
   2. User’s inventory count is decreased by one.
   3. User’s token increases by the price sold.
   
   

Write A Message on Tree Branch
-----------------
As a User, I want to write a message on a tree branch bought so that my message shows up on my tree branch in the Marketplace.

 - Priority: Medium
 - Estimate: 1 week
 - Confirmation:
 
   1. “You’ve successfully write a message on your tree branch” message pops up
   2. Tree branch message box is not empty
   3. User is redirected to Marketplace



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
 
 

