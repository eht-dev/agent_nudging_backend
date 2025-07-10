-- Complete sample_data.sql with table creation and sample data

-- Use the database
USE nudging_system;

-- Create tables first (in case they don't exist)
CREATE TABLE IF NOT EXISTS students (
   id INT PRIMARY KEY AUTO_INCREMENT,
   name VARCHAR(100) NOT NULL,
   email VARCHAR(150) UNIQUE NOT NULL,
   phone VARCHAR(20),
   timezone VARCHAR(50) DEFAULT 'UTC',
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS courses (
   id INT PRIMARY KEY AUTO_INCREMENT,
   name VARCHAR(200) NOT NULL,
   description TEXT,
   duration_weeks INT DEFAULT 12,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS enrollments (
   id INT PRIMARY KEY AUTO_INCREMENT,
   student_id INT,
   course_id INT,
   progress_percent DECIMAL(5,2) DEFAULT 0.00,
   last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (student_id) REFERENCES students(id),
   FOREIGN KEY (course_id) REFERENCES courses(id)
);

CREATE TABLE IF NOT EXISTS assignments (
   id INT PRIMARY KEY AUTO_INCREMENT,
   course_id INT,
   title VARCHAR(200) NOT NULL,
   description TEXT,
   due_date TIMESTAMP,
   points INT DEFAULT 100,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   FOREIGN KEY (course_id) REFERENCES courses(id)
);

CREATE TABLE IF NOT EXISTS submissions (
   id INT PRIMARY KEY AUTO_INCREMENT,
   student_id INT,
   assignment_id INT,
   submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   score DECIMAL(5,2),
   status VARCHAR(20) DEFAULT 'submitted',
   FOREIGN KEY (student_id) REFERENCES students(id),
   FOREIGN KEY (assignment_id) REFERENCES assignments(id)
);

CREATE TABLE IF NOT EXISTS nudges_log (
   id INT PRIMARY KEY AUTO_INCREMENT,
   student_id INT,
   nudge_type VARCHAR(50),
   message TEXT,
   channel VARCHAR(20),
   sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   opened_at TIMESTAMP NULL,
   action_taken BOOLEAN DEFAULT FALSE,
   FOREIGN KEY (student_id) REFERENCES students(id)
);

CREATE TABLE IF NOT EXISTS agent_configurations (
   id INT PRIMARY KEY AUTO_INCREMENT,
   agent_name VARCHAR(200) NOT NULL,
   agent_type VARCHAR(100) NOT NULL,
   database_config TEXT,
   query_config TEXT,
   template_config TEXT,
   schedule_config TEXT,
   channel_config TEXT,
   is_active BOOLEAN DEFAULT TRUE,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   last_run TIMESTAMP NULL,
   next_run TIMESTAMP NULL
);

CREATE TABLE IF NOT EXISTS agent_executions (
   id INT PRIMARY KEY AUTO_INCREMENT,
   agent_config_id INT,
   started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   completed_at TIMESTAMP NULL,
   status VARCHAR(50) DEFAULT 'running',
   items_processed INT DEFAULT 0,
   actions_taken INT DEFAULT 0,
   execution_log TEXT,
   FOREIGN KEY (agent_config_id) REFERENCES agent_configurations(id)
);

CREATE TABLE IF NOT EXISTS database_connections (
   id INT PRIMARY KEY AUTO_INCREMENT,
   connection_name VARCHAR(200) NOT NULL,
   database_type VARCHAR(50) NOT NULL,
   connection_string VARCHAR(500) NOT NULL,
   schema_cache TEXT,
   last_schema_refresh TIMESTAMP NULL,
   is_active BOOLEAN DEFAULT TRUE,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO students (name, email, phone, timezone) VALUES
('Alice Johnson', 'alice@example.com', '+1234567890', 'America/New_York'),
('Bob Smith', 'bob@example.com', '+1234567891', 'America/Los_Angeles'),
('Charlie Brown', 'charlie@example.com', '+1234567892', 'Europe/London'),
('Diana Prince', 'diana@example.com', '+1234567893', 'Asia/Tokyo'),
('Eve Wilson', 'eve@example.com', '+1234567894', 'Australia/Sydney'),
('Frank Miller', 'frank@example.com', '+1234567895', 'America/Chicago'),
('Grace Lee', 'grace@example.com', '+1234567896', 'Europe/Berlin'),
('Henry Davis', 'henry@example.com', '+1234567897', 'America/Denver'),
('Ivy Chen', 'ivy@example.com', '+1234567898', 'Asia/Shanghai'),
('Jack Wilson', 'jack@example.com', '+1234567899', 'Pacific/Auckland'),
('Kelly Brown', 'kelly@example.com', '+1234567800', 'America/New_York'),
('Liam Garcia', 'liam@example.com', '+1234567801', 'America/Los_Angeles'),
('Maya Patel', 'maya@example.com', '+1234567802', 'Asia/Mumbai'),
('Noah Kim', 'noah@example.com', '+1234567803', 'Asia/Seoul'),
('Olivia Martinez', 'olivia@example.com', '+1234567804', 'Europe/Madrid');

INSERT INTO courses (name, description, duration_weeks) VALUES
('Python Programming', 'Learn Python from basics to advanced concepts', 8),
('Data Science Fundamentals', 'Introduction to data science and analytics', 12),
('Web Development', 'Full-stack web development with modern frameworks', 16),
('Machine Learning', 'Introduction to ML algorithms and applications', 10),
('Database Design', 'Learn database design principles and SQL', 6),
('Mobile App Development', 'Build mobile apps for iOS and Android', 14),
('Digital Marketing', 'Complete digital marketing strategies', 8),
('Project Management', 'Agile and traditional project management', 10);

INSERT INTO enrollments (student_id, course_id, progress_percent, last_activity) VALUES
(1, 1, 85.50, '2024-07-09 14:30:00'),  -- Active student
(1, 2, 23.75, '2024-07-05 10:15:00'),  -- Falling behind
(2, 1, 78.25, '2024-07-09 09:45:00'),  -- Active student
(2, 3, 12.00, '2024-06-30 16:20:00'),  -- Very inactive
(3, 2, 67.80, '2024-07-08 11:30:00'),  -- Good progress
(3, 4, 34.20, '2024-07-06 13:45:00'),  -- Behind schedule
(4, 1, 95.50, '2024-07-09 08:20:00'),  -- Excellent student
(4, 5, 56.75, '2024-07-07 15:10:00'),  -- Average progress
(5, 3, 91.25, '2024-07-09 12:00:00'),  -- Excellent student
(5, 4, 45.60, '2024-07-04 14:30:00'),  -- Needs nudging
(6, 2, 15.20, '2024-06-25 09:00:00'),  -- Very inactive
(7, 1, 72.40, '2024-07-08 16:45:00'),  -- Good progress
(8, 3, 28.90, '2024-07-01 11:20:00'),  -- Falling behind
(9, 4, 88.75, '2024-07-09 10:15:00'),  -- Excellent
(10, 5, 41.30, '2024-07-05 13:30:00'), -- Needs encouragement
(11, 6, 65.80, '2024-07-08 14:20:00'), -- Good progress
(12, 7, 19.50, '2024-06-28 12:00:00'), -- Very behind
(13, 8, 83.20, '2024-07-09 09:30:00'), -- Doing well
(14, 1, 52.75, '2024-07-06 15:45:00'), -- Average
(15, 2, 76.90, '2024-07-08 17:20:00'); -- Good progress

INSERT INTO assignments (course_id, title, description, due_date, points) VALUES
(1, 'Python Basics Quiz', 'Test your understanding of Python fundamentals', '2024-07-15 23:59:59', 50),
(1, 'Data Structures Project', 'Implement basic data structures in Python', '2024-07-20 23:59:59', 100),
(1, 'Final Python Project', 'Build a complete Python application', '2024-07-25 23:59:59', 150),
(2, 'Statistics Assignment', 'Analyze sample dataset using statistical methods', '2024-07-18 23:59:59', 75),
(2, 'Data Visualization Project', 'Create interactive data visualizations', '2024-07-25 23:59:59', 100),
(3, 'HTML/CSS Portfolio', 'Build personal portfolio website', '2024-07-22 23:59:59', 100),
(3, 'JavaScript Calculator', 'Build interactive calculator app', '2024-07-28 23:59:59', 120),
(4, 'ML Algorithm Implementation', 'Implement linear regression from scratch', '2024-07-20 23:59:59', 100),
(5, 'Database Schema Design', 'Design database for e-commerce system', '2024-07-16 23:59:59', 80);

INSERT INTO submissions (student_id, assignment_id, score, status) VALUES
(1, 1, 85.50, 'graded'),
(2, 1, 92.25, 'graded'),
(4, 1, 78.75, 'graded'),
(7, 1, 88.00, 'graded'),
(14, 1, 76.50, 'graded'),
(1, 4, 88.00, 'graded'),
(3, 4, 95.25, 'graded'),
(15, 4, 82.75, 'graded'),
(4, 8, 91.50, 'graded'),
(9, 8, 87.25, 'graded');

-- Sample agent configuration for testing
INSERT INTO agent_configurations (
   agent_name, 
   agent_type, 
   database_config, 
   query_config,
   template_config,
   schedule_config,
   channel_config
) VALUES (
   'Student Engagement Monitor',
   'dynamic',
   '{"connection_string": "default"}',
   '{
       "main_table": "students",
       "joins": [
           {
               "table": "enrollments", 
               "join_type": "LEFT",
               "condition": "students.id = enrollments.student_id"
           }
       ],
       "conditions": [
           {
               "field": "enrollments.last_activity",
               "operator": "<",
               "value": "DATE_SUB(NOW(), INTERVAL 3 DAY)"
           },
           {
               "field": "enrollments.progress_percent",
               "operator": "<",
               "value": "50"
           }
       ],
       "select_fields": ["students.name", "students.email", "enrollments.last_activity", "enrollments.progress_percent"]
   }',
   '{
       "subject": "Don\'t fall behind, {{name}}!",
       "template": "Hi {{name}}, we noticed you haven\'t been active since {{last_activity}}. You\'re currently at {{progress_percent}}% progress. Let\'s get back on track!"
   }',
   '{
       "type": "interval",
       "minutes": 60
   }',
   '{
       "channels": ["email"],
       "primary": "email"
   }'
);

-- Sample nudge logs for testing
INSERT INTO nudges_log (student_id, nudge_type, message, channel, sent_at, action_taken) VALUES
(2, 'low_activity', 'Hi Bob, we noticed you haven\'t been active lately. Come back and continue learning!', 'email', '2024-07-08 10:00:00', FALSE),
(6, 'low_progress', 'Hi Frank, you\'re currently at 15% progress. Let\'s catch up!', 'email', '2024-07-07 14:30:00', TRUE),
(8, 'assignment_due', 'Hi Henry, your assignment is due tomorrow. Don\'t forget to submit!', 'sms', '2024-07-08 16:00:00', FALSE),
(12, 'engagement', 'Hi Liam, we miss you! Come back and continue your digital marketing course.', 'email', '2024-07-06 09:00:00', FALSE);

-- Sample database connection for testing
INSERT INTO database_connections (connection_name, database_type, connection_string, is_active) VALUES
('Local MySQL', 'mysql', 'mysql+pymysql://root:password@localhost:3306/lms_nudging_system', TRUE);

-- Show summary
SELECT 'Sample data inserted successfully!' as message;
SELECT 
   (SELECT COUNT(*) FROM students) as total_students,
   (SELECT COUNT(*) FROM courses) as total_courses,
   (SELECT COUNT(*) FROM enrollments) as total_enrollments,
   (SELECT COUNT(*) FROM assignments) as total_assignments,
   (SELECT COUNT(*) FROM agent_configurations) as sample_agents;