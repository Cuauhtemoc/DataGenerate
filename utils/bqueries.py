def getDashboards(dataset):
    query = f""" 
    SELECT organizations.name AS organization, COUNT(organization_charts.embed_url) AS Dashboards
    FROM 
       {dataset}.organizations LEFT JOIN
        {dataset}.organization_charts ON organization_charts.organization_id = organizations.id
        GROUP BY {dataset}.organization
    """ 
    return query

def getLoginOnce(dataset):
    query = f"""SELECT organizations.name AS organization, FLOOR(COUNT(users.last_login)/NULLIF(COUNT(users.organization_id),0) * 100) AS Login_Percentage
                FROM
                    {dataset}.organizations 
                    LEFT JOIN
                    {dataset}.users ON users.organization_id = organizations.id
                GROUP BY organization"""
    return query

def getLoginWeek(dataset):
    query = f""" 
            SELECT organizations.name AS organization, FLOOR(SUM(CASE WHEN users.last_login > TIMESTAMP_SUB(CURRENT_TIMESTAMP(),INTERVAL 7 DAY) THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN users.id IS NOT NULL THEN 1 ELSE 0 END), 0) * 100) as last_login_week
          FROM 
            {dataset}.organizations LEFT JOIN
            {dataset}.users ON users.organization_id = organizations.id 
            GROUP BY organization  
        """
    return query

def getLoginMonth(dataset):
    query = f""" 
            SELECT organizations.name AS organization, FLOOR(SUM(CASE WHEN users.last_login > TIMESTAMP_SUB(CURRENT_TIMESTAMP(),INTERVAL 28 DAY) THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN users.id IS NOT NULL THEN 1 ELSE 0 END), 0) * 100) as last_login_month
          FROM 
            {dataset}.organizations LEFT JOIN
            {dataset}.users ON users.organization_id = organizations.id 
            GROUP BY organization  
        """
    return query

def getLoginRange(dataset,inter):
    query = f""" 
            SELECT organizations.name AS organization, FLOOR(SUM(CASE WHEN users.last_login > TIMESTAMP_SUB(CURRENT_TIMESTAMP(),INTERVAL {inter} DAY) THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN users.id IS NOT NULL THEN 1 ELSE 0 END), 0) * 100) as last_login_{inter}_days
          FROM 
            {dataset}.organizations LEFT JOIN
            {dataset}.users ON users.organization_id = organizations.id 
            GROUP BY organization  
        """
    return query

def getGoals(dataset):
    query = f""" 
        SELECT organizations.name AS organization, COUNT(goals.status_id) AS goals
        FROM 
            {dataset}.organizations LEFT JOIN
            {dataset}.goals ON goals.organization_id = organizations.id
        GROUP BY organization  
        """
    return query

def getGoalsCycles():
    query= f""" 
        SELECT organizations.name AS organization,IFNULL(COUNT(DISTINCT cycles.goal_id),0) AS goals_with_cycle
            FROM(
                {dataset}.goals 
                INNER JOIN 
                {dataset}.cycles ON cycles.goal_id = goals.id 
                FULL JOIN
                {dataset}t.organizations ON organization_id = organizations.id
            )
            GROUP BY organization
        """
    return query

def getGoalsCyclesActions(dataset):
    query= f""" 
            WITH cte AS (SELECT organizations.name AS organization, goals.id AS goals, cycles.id AS cycle, actions.id AS actions 
                FROM(
                    {dataset}.actions 
                    INNER JOIN
                    {dataset}.cycles ON actions.cycle_id = cycles.id 
                    INNER JOIN 
                    {dataset}.goals ON cycles.goal_id = goals.id 
                    FULL JOIN
                    {dataset}.organizations ON goals.organization_id = organizations.id
                    )
                GROUP BY organization, goals, cycle, actions)
                SELECT organization, COUNT(DISTINCT goals) AS goals_with_cycle_actions
                FROM cte
                GROUP BY organization
            """
    return query

def getGoalInProgress(dataset):
    query=f""" 
       SELECT organizations.name AS organization, COUNT(goals.status_id) AS goal_in_progress    
            FROM 
            {dataset}.goals 
            FULL JOIN
            {dataset}.organizations ON goals.organization_id = organizations.id AND goals.status_id = 5
            GROUP BY organization
            """
    return query

def getCycleInProgress(dataset):
    query=f""" 
        SELECT organizations.name AS organization, COUNT(cycles.status_id) AS cycle_in_progress
            FROM {dataset}.cycles 
            LEFT JOIN
            {dataset}.goals ON cycles.goal_id = goals.id AND cycles.status_id=5
            FULL JOIN
            {dataset}.organizations ON goals.organization_id = organizations.id 
            GROUP BY organization
        """
    return query

def getActionInProgress(dataset):
    query=f""" 
       SELECT organizations.name AS organization, COUNT(actions.status_id) AS action_in_progress    
            FROM {dataset}.actions 
            LEFT JOIN
            {dataset}.cycles ON actions.cycle_id = cycles.id AND actions.status_id = 2
            LEFT JOIN
            {dataset}.goals ON cycles.goal_id = goals.id 
            FULL JOIN
            {dataset}.organizations ON goals.organization_id = organizations.id 
            GROUP BY organization
        """
    return query

def getGoalCycleSubmitted():
    query=f"""
        SELECT organizations.name AS organization, COUNT(cycles.status_id) as goals_cycles_submitted
            FROM  {dataset}.cycles 
            LEFT JOIN
            {dataset}.goals ON cycles.goal_id = goals.id AND cycles.status_id=2 AND goals.status_id=2
            FULL JOIN
            {dataset}.organizations ON goals.organization_id = organizations.id 
            GROUP BY organization
            ORDER BY 1
        """
    return query

def getGoalsClosed(dataset):
    query=f""" 
       SELECT organizations.name AS organization, COUNT(goals.status_id) AS goals_closed    
            FROM 
            {dataset}.goals 
            FULL JOIN
            {dataset}.organizations ON goals.organization_id = organizations.id AND goals.status_id = 7
            GROUP BY organization
        """
    return query

def getCyclesClosed(dataset):
    query=f""" 
        SELECT organizations.name AS organization, COUNT(cycles.status_id) AS cycle_closed
            FROM {dataset}.cycles 
            LEFT JOIN
            {dataset}.goals ON cycles.goal_id = goals.id AND cycles.status_id=7
            FULL JOIN
            {dataset}.organizations ON goals.organization_id = organizations.id 
            GROUP BY organization
        """
    return query

def getOffTrack(dataset):
    query = f""" 
       SELECT organizations.name AS organization, SUM(CASE WHEN actions.end_date < CURRENT_TIMESTAMP then 1 else 0 END)/NULLIF(sum(CASE WHEN actions.start_date IS NOT NULL THEN 1 ELSE 0 end), 0) * 100 as actions_off_track
            FROM {dataset}.actions
            INNER JOIN 
            {dataset}.cycles ON cycles.id = actions.cycle_id
            INNER JOIN
            {dataset}.goals ON goals.id =cycles.goal_id 
            FULL JOIN 
            {dataset}.organizations ON organizations.id = goals.organization_id 
        GROUP BY organization
        """
    return query

def getMilestonesCompleted(dataset):
    query = f"""
        SELECT organizations.name AS organization,  SUM(CASE WHEN milestones.completed = 1 THEN 1 ELSE 0 END)/NULLIF(COUNT(milestones.completed),0) * 100 AS miletones_completed_percentage
            FROM {dataset}.organizations
            LEFT JOIN 
            {dataset}.milestones ON milestones.organization_id = organizations.id
            GROUP BY organization 
    """

def nextMileStoneDate(dataset):
    query=f"""
        SELECT organizations.name AS organization, MIN(milestones.due_on) AS next_milestone_date
            FROM {dataset}.milestones
            LEFT JOIN
            {dataset}.organizations ON milestones.organization_id = organizations.id
            WHERE milestones.due_on <= CURRENT_DATE AND milestones.completed = 0  
            GROUP BY organization
    """

def getAll(dataset):
    query=f""" 
        WITH table_1 AS (
            SELECT organizations.name AS tbl1_organization,  SUM(CASE WHEN milestones.completed = 1 THEN 1 ELSE 0                     END)/NULLIF(COUNT(milestones.completed),0) *  100 AS milestones_completed_percentage
            FROM {dataset}.organizations
            LEFT JOIN 
            {dataset}.milestones ON milestones.organization_id = organizations.id
            GROUP BY tbl1_organization), 
            table_2 AS (
                    SELECT organizations.name AS tbl2_organization, COUNT(organization_charts.embed_url) AS dashboards,  
                    FROM 
                    {dataset}.organizations LEFT JOIN
                        {dataset}.organization_charts ON organization_charts.organization_id = organizations.id
                        GROUP BY tbl2_organization),
            table_3 AS(
                    SELECT organizations.name AS tbl3_organization, FLOOR(COUNT(users.last_login)/NULLIF(COUNT(users.organization_id),0) * 100) AS login_Percentage
                    FROM
                        {dataset}.organizations 
                        LEFT JOIN
                        {dataset}.users ON users.organization_id = organizations.id
                    GROUP BY tbl3_organization
            ),
            table_4 AS(
                    SELECT organizations.name AS tbl4_organization, FLOOR(SUM(CASE WHEN users.last_login > TIMESTAMP_SUB(CURRENT_TIMESTAMP(),INTERVAL 7 DAY) THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN users.id IS NOT NULL THEN 1 ELSE 0 END), 0) * 100) as last_login_week
                    FROM 
                        {dataset}.organizations LEFT JOIN
                        {dataset}.users ON users.organization_id = organizations.id 
                        GROUP BY tbl4_organization 
            ),
            table_5 AS(
                        SELECT organizations.name AS tbl5_organization, FLOOR(SUM(CASE WHEN users.last_login > TIMESTAMP_SUB(CURRENT_TIMESTAMP(),INTERVAL 28 DAY) THEN 1 ELSE 0 END)/NULLIF(SUM(CASE WHEN users.id IS NOT NULL THEN 1 ELSE 0 END), 0) * 100) as last_login_month
                    FROM 
                        {dataset}.organizations LEFT JOIN
                        {dataset}.users ON users.organization_id = organizations.id 
                        GROUP BY tbl5_organization  
            ),

            table_7 AS(
                    SELECT organizations.name AS tbl7_organization, COUNT(goals.status_id) AS goals
                    FROM 
                        {dataset}.organizations LEFT JOIN
                        {dataset}.goals ON goals.organization_id = organizations.id
                    GROUP BY tbl7_organization  
            ),
            table_8 AS(
                    SELECT organizations.name AS tbl8_organization,IFNULL(COUNT(DISTINCT cycles.goal_id),0) AS goals_with_cycle
                    FROM(
                        {dataset}.goals 
                        INNER JOIN 
                        {dataset}.cycles ON cycles.goal_id = goals.id 
                        FULL JOIN
                        {dataset}.organizations ON organization_id = organizations.id
                    )
                    GROUP BY tbl8_organization
            ),
            table_9 AS(
                    WITH cte AS (SELECT organizations.name AS tbl9_organization, goals.id AS goals, cycles.id AS cycle, actions.id AS actions 
                        FROM(
                            {dataset}.actions 
                            INNER JOIN
                            {dataset}.cycles ON actions.cycle_id = cycles.id 
                            INNER JOIN 
                            {dataset}.goals ON cycles.goal_id = goals.id 
                            FULL JOIN
                            {dataset}.organizations ON goals.organization_id = organizations.id
                            )
                        GROUP BY tbl9_organization, goals, cycle, actions)
                        SELECT tbl9_organization, COUNT(DISTINCT goals) AS goals_with_cycle_actions
                        FROM cte
                        GROUP BY tbl9_organization
            ),
            table_10 AS(
                    SELECT organizations.name AS tbl10_organization, COUNT(goals.status_id) AS goal_in_progress    
                        FROM 
                        {dataset}.goals 
                        FULL JOIN
                        {dataset}.organizations ON goals.organization_id = organizations.id AND goals.status_id = 5
                        GROUP BY tbl10_organization
            ),
            table_11 AS(
                    SELECT organizations.name AS tbl11_organization, COUNT(cycles.status_id) AS cycle_in_progress
                        FROM {dataset}.cycles 
                        LEFT JOIN
                        {dataset}.goals ON cycles.goal_id = goals.id AND cycles.status_id=5
                        FULL JOIN
                        {dataset}.organizations ON goals.organization_id = organizations.id 
                        GROUP BY tbl11_organization
            ),
            table_12 AS(
                SELECT organizations.name AS tbl12_organization, COUNT(actions.status_id) AS action_in_progress    
                        FROM {dataset}.actions 
                        LEFT JOIN
                        {dataset}.cycles ON actions.cycle_id = cycles.id AND actions.status_id = 2
                        LEFT JOIN
                        {dataset}.goals ON cycles.goal_id = goals.id 
                        FULL JOIN
                        {dataset}.organizations ON goals.organization_id = organizations.id 
                        GROUP BY tbl12_organization
            ),
            table_13 AS(
                    SELECT organizations.name AS tbl13_organization, COUNT(cycles.status_id) as goals_cycle_submitted
                        FROM  {dataset}.cycles 
                        LEFT JOIN
                        {dataset}.goals ON cycles.goal_id = goals.id AND cycles.status_id=2 AND goals.status_id=5
                        FULL JOIN
                        {dataset}.organizations ON goals.organization_id = organizations.id 
                        GROUP BY tbl13_organization
                        ORDER BY 1
            ),
            table_14 AS(
                SELECT organizations.name AS tbl14_organization, COUNT(goals.status_id) AS goals_closed    
                        FROM 
                        {dataset}.goals 
                        FULL JOIN
                        {dataset}.organizations ON goals.organization_id = organizations.id AND goals.status_id = 7
                        GROUP BY tbl14_organization
            ),
            table_15 AS(
                    SELECT organizations.name AS tbl15_organization, COUNT(cycles.status_id) AS cycles_closed
                        FROM {dataset}.cycles 
                        LEFT JOIN
                        {dataset}.goals ON cycles.goal_id = goals.id AND cycles.status_id=7
                        FULL JOIN
                        {dataset}.organizations ON goals.organization_id = organizations.id 
                        GROUP BY tbl15_organization
            ),
            table_16 AS(
                SELECT organizations.name AS tbl16_organization, SUM(CASE WHEN actions.end_date < CURRENT_TIMESTAMP then 1 else 0 END)/NULLIF(sum(CASE WHEN actions.start_date IS NOT NULL THEN 1 ELSE 0 end), 0) * 100 as percentage_off_track
                        FROM {dataset}.actions
                        INNER JOIN 
                        {dataset}.cycles ON cycles.id = actions.cycle_id
                        INNER JOIN
                        {dataset}.goals ON goals.id =cycles.goal_id 
                        FULL JOIN 
                        {dataset}.organizations ON organizations.id = goals.organization_id 
                    GROUP BY tbl16_organization
            ),
            table_17 AS(
                    SELECT organizations.name AS tbl17_organization,  SUM(CASE WHEN milestones.completed = 1 THEN 1 ELSE 0 END)/NULLIF(COUNT(milestones.completed),0) * 100 AS miletones_completed_percentage
                        FROM {dataset}.organizations
                        LEFT JOIN 
                        {dataset}.milestones ON milestones.organization_id = organizations.id
                        GROUP BY tbl17_organization 
            ),
            table_18 AS(
                    SELECT organizations.name AS tbl18_organization, MIN(milestones.due_on) AS next_milestone_date
                        FROM {dataset}.milestones
                        LEFT JOIN
                        {dataset}.organizations ON milestones.organization_id = organizations.id
                        WHERE milestones.due_on <= CURRENT_DATE AND milestones.completed = 0  
                        GROUP BY tbl18_organization
            )
            SELECT tbl1_organization AS organization, dashboards, milestones_completed_percentage,login_Percentage,last_login_week,last_login_month,goals,goals_with_cycle,goals_with_cycle_actions,cycle_in_progress,action_in_progress,goals_cycle_submitted,goals_closed,cycles_closed,percentage_off_track,miletones_completed_percentage,  next_milestone_date
            FROM table_1
            LEFT JOIN table_2 ON table_1.tbl1_organization = table_2.tbl2_organization
            LEFT JOIN table_3 ON table_2.tbl2_organization = table_3.tbl3_organization
            LEFT JOIN table_4 ON table_3.tbl3_organization = table_4.tbl4_organization
            LEFT JOIN table_5 ON table_4.tbl4_organization = table_5.tbl5_organization
            LEFT JOIN table_7 ON table_5.tbl5_organization = table_7.tbl7_organization
            LEFT JOIN table_8 ON table_7.tbl7_organization = table_8.tbl8_organization
            LEFT JOIN table_9 ON table_8.tbl8_organization = table_9.tbl9_organization
            LEFT JOIN table_10 ON table_9.tbl9_organization = table_10.tbl10_organization
            LEFT JOIN table_11 ON table_10.tbl10_organization = table_11.tbl11_organization
            LEFT JOIN table_12 ON table_11.tbl11_organization = table_12.tbl12_organization
            LEFT JOIN table_13 ON table_12.tbl12_organization = table_13.tbl13_organization
            LEFT JOIN table_14 ON table_13.tbl13_organization = table_14.tbl14_organization
            LEFT JOIN table_15 ON table_14.tbl14_organization = table_15.tbl15_organization
            LEFT JOIN table_16 ON table_15.tbl15_organization = table_16.tbl16_organization
            LEFT JOIN table_17 ON table_16.tbl16_organization = table_17.tbl17_organization
            LEFT JOIN table_18 ON table_17.tbl17_organization = table_18.tbl18_organization
    """ 