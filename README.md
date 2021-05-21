# Cloud-Computing

Task:  
Implement a serverless, microservice-driven web application. 
Specifically, you will build a Dining Concierge chatbot that sends you restaurant suggestions based on a set of preferences that you provide the chatbot with
through conversation.

Architecture Diagram:
<br><img src = "https://user-images.githubusercontent.com/38934646/119186307-827e0380-ba3d-11eb-95cf-d073c49873ee.png" width = "500">

AWS Services used:
1. S3
2. API Gateway
3. Lambda
4. Lex
5. SQS
6. SNS
7. DynamoDB
8. ElasticSearch

Example Interaction:

User: Hello
<br>Bot: Hi there, how can I help?
<br>User: I need some restaurant suggestions.
<br>Bot: Great. I can help you with that. What city or city area are you looking to dine in?
<br>User: Manhattan
<br>Bot: Got it, Manhattan. What cuisine would you like to try?
<br>User: Japanese
<br>Bot: Ok, how many people are in your party?
<br>User: Two
<br>Bot: A few more to go. What date?
<br>User: Today
<br>Bot: What time?
<br>User: 7 pm, please
<br>Bot: Great. Lastly, I need your phone number so I can send you my findings.
<br>User: 123-456-7890
<br>Bot: You’re all set. Expect my suggestions shortly! Have a good day.
<br>User: Thank you!
<br>Bot: You’re welcome.

(a few minutes later)
<br>User gets the following text message:
<br>“Hello! Here are my Japanese restaurant suggestions for 2 people, for today at 7 pm: 1. Sushi Nakazawa, located at 23 Commerce St, 2. Jin Ramen, located at 3183 Broadway, 3. Nikko, located at 1280 Amsterdam Ave. Enjoy your meal!”


