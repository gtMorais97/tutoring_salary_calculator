# tutoring_salary_calculator

I have been tutoring programming students for a while and so decided to use the google calendar api to calculate how much money I have earned from this side job between two dates. The script also tells me what proportion of time I spent with each student in a nice little pie chart. 


If you want to use it, add your tutoring appointments to your calendar. As it is, it will only work if all your appointments start with 'Explica', but you can change that in the file monings_calculator.py in line 81 by replacing 'Explica' with whatever you want.


How to run:


1.go to the explicacoes dir


2.run ```python3 monings_calculator.py start_date end_date price_per_hour``` with dd/mm/yyyy format and price_per_hour should be a number (duh).
