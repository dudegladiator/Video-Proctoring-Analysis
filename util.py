def get_score_color(score):
    """Get color based on score"""
    print(score)
    if score >= 75:
        return "#D32F2F"  # Darker red
    elif score >= 50:
        return "#F57C00"  # Darker orange
    elif score >= 25:
        return "#FBC02D"  # Darker yellow
    else:
        return "#388E3C"  # Darker green
    
    
def get_score_status(score):
    """Get status based on score"""
    # 'High Risk', 'Medium Risk', 'Low Risk', 'No Risk'
    if score >= 75:
        return "High Risk"
    elif score >= 50:
        return "Medium Risk"
    elif score >= 25:
        return "Low Risk"
    else:
        return "No Risk"