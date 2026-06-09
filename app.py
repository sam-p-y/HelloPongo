import streamlit as st
import json
from google import genai
from google.genai import types

# 1. Setup the App Interface
st.set_page_config(page_title="Our Kitchen", page_icon="🍳", layout="centered")
st.title("Our Kitchen")

# 2. Securely connect the Gemini VIP Pass
API_KEY = st.secrets.get("GEMINI_API_KEY")
if not API_KEY:
    st.error("API Key missing! Please add it to your Streamlit secrets.")
    st.stop()

client = genai.Client(api_key=API_KEY)

# 3. The Input Section
with st.expander("📝 Plan This Week", expanded=True):
    meals_needed = st.number_input("Meals Needed", min_value=1, max_value=7, value=4)
    schedule_notes = st.text_area("Schedule Notes", placeholder="e.g., Tuesday 20 mins to cook...")
    inventory = st.text_area("Inventory to Use", placeholder="e.g., Half a bag of rice, cheddar cheese...")
    cravings = st.text_area("Cravings & Goals", placeholder="e.g., Healthy, Tex-Mex...")
    
    generate_button = st.button("Generate Meals", type="primary", use_container_width=True)

# 4. The Brain (Talking to Gemini with strict formatting rules)
if generate_button:
    with st.spinner("Chef Gemini is doing the puzzle math..."):
        prompt = f"""
        You are an expert meal planner. The user needs {meals_needed} meals.
        Schedule Notes: {schedule_notes}
        Inventory: {inventory}
        Cravings: {cravings}
        
        Rules:
        1. Use the Capsule Grocery Strategy to cross-utilize ingredients.
        2. Provide a reliable, generalized food image URL from Unsplash using this format: 
           https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600 (or similar valid food photos).
        3. For instructions, break them into clear, actionable steps inside a JSON array.
        4. Explicitly state the exact quantities needed for this specific recipe inside the 'recipe_ingredients' array.
        5. In 'source_inspiration', declare which cooking methodology or established site style (e.g., 'Serious Eats Food Lab style', 'Traditional Italian Method') this logic is built on.
        
        You MUST output valid JSON matching this exact structure:
        {{
          "meals": [
            {{
              "day": "Monday",
              "name": "Meal Name",
              "time": "30 mins",
              "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600",
              "source_inspiration": "Inspired by Serious Eats' structural layout for pan-searing.",
              "recipe_ingredients": [
                "1 lb Chicken Breast",
                "2 Bell Peppers",
                "1/2 teaspoon Cumin"
              ],
              "instructions": [
                "Slice the chicken and bell peppers into thin strips.",
                "Heat oil in a heavy skillet over high heat until smoking.",
                "Cook chicken for 5 minutes, remove, then sear peppers."
              ]
            }}
          ],
          "groceries": [
            {{
              "aisle": "Produce",
              "items": ["2 Yellow Onions", "1 Lime"]
            }}
          ]
        }}
        """
        
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.7
                )
            )
            st.session_state.data = json.loads(response.text)
        except Exception as e:
            st.error(f"There was an error: {e}")

# 5. The Output (The Refined App Screen)
if "data" in st.session_state:
    data = st.session_state.data
    
    st.divider()
    st.header("🍽️ Your Weekly Gallery")
    
    for meal in data.get("meals", []):
        st.subheader(f"{meal['day']}: {meal['name']}")
        st.caption(f"⏱️ Prep time: {meal['time']} | 💡 {meal.get('source_inspiration', 'Standard Recipe Pattern')}")
        
        if meal.get("image_url"):
            st.image(meal["image_url"], use_container_width=True)
            
        with st.expander("View Recipe Details", expanded=False):
            st.write("**Ingredients Needed for This Recipe:**")
            for ing in meal.get("recipe_ingredients", []):
                st.write(f"- {ing}")
                
            st.write("**Step-by-Step Instructions:**")
            for i, step in enumerate(meal.get("instructions", []), 1):
                st.write(f"{i}. {step}")
            
    st.divider()
    st.header("🛒 Tap-to-Check Grocery List")
    
    for aisle in data.get("groceries", []):
        st.subheader(aisle["aisle"])
        for item in aisle["items"]:
            st.checkbox(item, key=f"{aisle['aisle']}_{item}")
