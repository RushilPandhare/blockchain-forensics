# blockchain-forensics

The goal of this project is to make cryptocurrency analysis much easier for users who are just getting into blockchain forensics, but dont know how to create proper graphs for investigation or if they just want to see the potential malicious transactions made by just entering a bitcoin address. We have used Isolation Forest which is an algorithm used specifically to detect any anomalies based on the transactions being a large amount in a single transaction or many transactions in small amounts


To run the program, just run graph.py which will then ask you to enter the bitcoin address. Upon adding it, the program will give you the suspicious transactions detected according to Isolation Forest and based on its predictions, it will display a simple graphs, displaying the inputs , outputs and suspicious transactions