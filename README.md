# AI‑Integrated Scalable Support System
>**Note**:The project is currently in the development stage. At the moment, nothing is functional. We are trying to make progress, but time constraints are a major challenge.

A high‑performance, AI‑enabled support‑ticket platform combining a Django/DRF backend with a modern React frontend. It automates ticket distribution, forecasts load, and dynamically merges teams to optimize resource use. 

## What is this?

This repository contains the source for a scalable support system backend (Django + DRF) paired with a single‑page React application. It handles high ticket volumes, provides role‑based access, integrates AI for traffic forecasting, and supports automatic department merging.


## What are we building?

- **Scalable Ticket Queue**  
  Automatic load distribution across agents using round‑robin and least‑busy strategies.  
- **Role‑Based Access Control**  
  JWT authentication with fine‑grained permissions for agents and admins.  
- **AI‑Driven Traffic Forecasting**  
  A time‑series model predicts next‑hour ticket volume to inform scaling decisions.  
- **Automatic Department Merging**  
  Dynamically redistributes tickets from overloaded to underutilized teams based on thresholds.  
- **React Frontend**  
  A responsive SPA built with React (Create React App), Redux/Context API, and Axios for seamless interaction with backend APIs.  

---

## Architecture
>![image](https://github.com/user-attachments/assets/cd2c9b9e-dc6d-4de0-b18e-dce988370619)

## Ticket Processing Logic
When a user creates a ticket:

1. The system identifies the appropriate department based on the issue or request type.
2. It checks the current traffic of all agents in that department.
3. A load distribution algorithm (round-robin or least-busy) assigns the ticket to the optimal agent.
4. If no agents are available or the department is overloaded:
   - The ticket is placed in a queue (`TicketQueue`) for pending processing.
   - A merge suggestion may be triggered if the department exceeds its traffic threshold.
5. Assigned agents can update the ticket's status, and traffic counts are adjusted accordingly.

The goal is to ensure **fair workload distribution**, **faster resolution times**, and **system stability under high load**.

>![30109309675](https://github.com/user-attachments/assets/c414c5d7-495b-45da-8613-1f9426c6d385)

Built with scalability, AI, and clean architecture in mind.