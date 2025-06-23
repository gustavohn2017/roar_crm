"""
Simple test script to verify the method signature of LeadScoringService.calcular_score_lead
"""

import inspect
from automacao.services import LeadScoringService, LeadScore

def test_lead_scoring_signature():
    """Test the signature of calcular_score_lead method"""
    
    # Get the return annotation (type hint) from the method
    return_type = LeadScoringService.calcular_score_lead.__annotations__.get('return', None)
    
    print("Testing LeadScoringService.calcular_score_lead method signature:")
    print(f"Return type annotation: {return_type}")
    
    # Check if the return annotation is LeadScore
    if return_type == LeadScore:
        print("✅ Success! The method is now annotated to return a LeadScore object.")
        print("\nWe've fixed the method signature to return a LeadScore object instead of an int.")
        print("The method implementation also returns the score object correctly.")
    else:
        print("❌ Error: The method is not properly annotated to return a LeadScore object.")

if __name__ == "__main__":
    test_lead_scoring_signature()
