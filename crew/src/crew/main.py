from school_crew import schoolcrew

crew_instance = schoolcrew()

inputs = {
    "location": input("Enter the location you are looking for schools : ") or "Bangalore | use my current location",
    "grade": input("Enter the grade you are interested in (e.g., 1st Grade): ") or "1st Grade",
    "curriculum": input("Enter the curriculum you prefer (e.g., CBSE, ICSE): ") or "CBSE"
}

result = crew_instance.crew().kickoff(inputs=inputs)

# Print final result
print("\n\n✅ Final Travel Plan Output:\n")
print(result)
