  # Iteration 5: Report

## Responsibilites
- Buy a Tree Branch: Ted, Bhavin, Nico
Implement the basics of a buy and sell system for users. By the end of this iteration, the plan is to have some system for tracking the ownership of a branch.
- Write a Message on Tree Branch: Nico, Bhavin, Ted
After laying the groundwork for tracking the ownership of branches, allows users to write custom messages on any of the branches they own.
- Signup improvements: Ted
Pre-populating non-password fields after getting invalid password message
- Cairo tree generation: Bhavin, Nico
Ted:
- work on viewing inventory feature

## Completed
We completed polishing up the sign up and login feature from the previous iteration. We used bootstrap to clean up the UI,
and make it more responsive. For example, on the signup page when there is some sort of error processing a request to sign up,
the data fields other than the password are all pre-filled in the response. 

For the backend side of things, we also completed the tree generation at different zoom levels with Cairo. Right now the 
flask application accepts a command line argument of `render-tree` with further options like zoom level and maximum tree 
depth specified with `--zoom` and `--depth`. A PNG and SVG image will be saved to the `static/images` directory with the name
`tree_z<zoom-level>.png|svg`. We weren't able to reach the stage where we can add branches to the database this week, but
should get to and much more by next week with thanks giving break down the pipe. The only thing left to do is partition the images of the tree at different zoom levels into
tiles and store those to disk along with information about the branches contained in each tile. In order to implement this,
we needed a function that determines if two rectangles of arbritrary orientation intersect. We were able to implement that function
this week. Once we have the branches in the database, we should be able to quickly get through the backlog of user stories about
buying and selling that has been piling over the previous iterations. 

## Problems and Struggles
We learned the importance of committing your work frequently _and_ pushing it to remote in case something bad happens. One of
the team members accidentally deleted his local repository that had several commits that were not pushed to remote (`rm` does not
seem to provide an undo, so all the code had to be re-rewritten). This mistake should not happen again, since `rm` has now been
aliased to another trash management utility that has restore capabilties.


## Plan for Iteration 5
 - Add branches to database: Bhavin, Nico
 - Render tree on the client side by requesting pre-rendered tiles from the app
 - Buy a Tree Branch: Ted, Bhavin, Nico
Implement the basics of a buy and sell system for users. By the end of this iteration, the plan is to have some system for tracking the ownership of a branch.
- Write a Message on Tree Branch: Nico, Bhavin, Ted
After laying the groundwork for tracking the ownership of branches, allows users to write custom messages on any of the branches they own.

## Plan for Iteration 6
- Finish work on  the buy and sell system for branches: Ted, Bhavin, Nico
- Work on making the website look visually attractive, and since it will be unlikely that we will have all the plans for previous Iterations completed, work on finishing those.
Work on User Interaction: Put finishing touches and polish user interactions. By the end of this iteration, the plan is to have the user interactions with the application smooth and look nice.

## Plan for Iteration 7
Continue making UI improvements, and polishing the website by restructuring the website, fixing any glitches or hiccups, and possibly using CSS/Javascript animations to make the user experience feel smooth since it is unlikely that it will as poslished as we would want it to be with just one week of work.
Work on features/user stories that were not completed from the previous iteration.
