# ShopBot User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Using ShopBot](#using-shopbot)
4. [Features Guide](#features-guide)
5. [Tips for Best Results](#tips-for-best-results)
6. [Troubleshooting](#troubleshooting)
7. [Privacy & Data](#privacy--data)
8. [FAQ](#faq)

---

## Introduction

### What is ShopBot?

ShopBot is an intelligent conversational shopping assistant that helps you find the perfect products from Amazon's catalog through natural conversation. Instead of browsing through hundreds of products, simply tell ShopBot what you're looking for, and it will ask clarifying questions to understand your needs and recommend the best options.

### Key Features

- **Natural Conversation**: Chat naturally about what you need
- **Smart Questions**: ShopBot asks targeted questions to understand your preferences
- **Personalized Recommendations**: Get product suggestions tailored to your needs
- **Comparison Tables**: See side-by-side comparisons of top products
- **Explainable Results**: Understand why each product was recommended
- **Real-Time Data**: Access to current product information, prices, and ratings

### Who Should Use ShopBot?

- Online shoppers looking for product recommendations
- Users who want personalized shopping assistance
- Anyone overwhelmed by too many product choices
- Shoppers who value expert guidance in their purchases

---

## Getting Started

### System Requirements

**Web Browser** (any modern browser):
- Google Chrome 90+
- Mozilla Firefox 88+
- Safari 14+
- Microsoft Edge 90+

**Internet Connection**: Stable broadband connection recommended

### Accessing ShopBot

1. Open your web browser
2. Navigate to: `http://localhost:3000` (or your deployment URL)
3. The ShopBot interface will load automatically

### First Time Setup

No registration or login required! Simply start chatting.

---

## Using ShopBot

### Starting a Conversation

1. **Open ShopBot** in your browser
2. **Type your request** in the message box at the bottom
3. **Press Enter** or click the Send button

**Example Opening Messages:**
```
"I need a laptop for college"
"Looking for wireless headphones"
"I want to buy a gift for my mom"
"Need a USB cable for my phone"
```

### The Conversation Flow

ShopBot follows a structured approach to help you find the right product:

#### Step 1: Initial Request
You tell ShopBot what you're looking for.

**Example:**
```
You: "I need a laptop"
```

#### Step 2: Clarifying Questions
ShopBot asks questions to understand your needs (typically 2-5 questions).

**Example:**
```
ShopBot: "What's your budget for the laptop?"
You: "Around $800"

ShopBot: "What will you primarily use it for?"
You: "Programming and web development"
```

#### Step 3: Recommendations
Once ShopBot has enough information, it provides personalized recommendations with:
- **Product names and images**
- **Prices and discounts**
- **Ratings and review counts**
- **Key features**
- **Comparison table**
- **Explanation of why each product fits your needs**

#### Step 4: Follow-up
You can ask follow-up questions or request different options.

**Example:**
```
You: "Do you have anything cheaper?"
You: "What about gaming laptops?"
You: "Tell me more about the first option"
```

---

## Features Guide

### 1. Product Search

ShopBot can search across multiple product categories:

**Electronics**
- Computers & Accessories
- Mobile Phones & Accessories
- Cameras & Photography
- Audio & Video
- Home Theater & TV

**Home & Kitchen**
- Appliances
- Furniture
- Kitchen & Dining
- Home Décor

**And many more categories...**

### 2. Filtering Options

ShopBot considers multiple factors when recommending products:

#### Budget/Price Range
```
You: "Under $50"
You: "Between $100 and $200"
You: "Around $500"
```

#### Product Category
```
You: "Electronics"
You: "Computers & Accessories"
You: "Mobile Accessories"
```

#### Use Case
```
You: "For gaming"
You: "For professional photography"
You: "For everyday use"
You: "As a gift"
```

#### Quality Requirements
```
You: "Highly rated products only"
You: "At least 4 stars"
You: "Best quality available"
```

#### Specific Features
```
You: "Waterproof"
You: "Wireless"
You: "Fast charging"
You: "Noise cancelling"
```

### 3. Product Comparison

When ShopBot recommends products, you'll see a comparison table showing:

| Attribute | Product 1 | Product 2 | Product 3 |
|-----------|-----------|-----------|-----------|
| **Price** | $45.99 | $52.00 | $38.50 |
| **Rating** | 4.5 | 4.3 | 4.6 |
| **Reviews** | 12,450 | 8,320 | 15,678 |
| **Discount** | 25% | 15% | 30% |
| **Key Features** | Feature highlights for each product |

### 4. Product Details

Each recommendation includes:

- **Product Name**: Full product title
- **Price Information**: 
  - Current discounted price
  - Original price (if applicable)
  - Discount percentage
- **Rating**: Star rating (0-5)
- **Review Count**: Number of customer reviews
- **Key Features**: Top 3 most important features
- **Product Image**: Visual preview
- **Product Link**: Direct link to Amazon product page

### 5. Currency Display

Prices are displayed in USD by default. The system converts from the original currency (INR) automatically.

---

## Tips for Best Results

### 1. Be Specific About Your Needs

❌ **Vague**: "I need something"
✅ **Specific**: "I need a USB-C cable for fast charging my Samsung phone"

### 2. Mention Your Budget Early

✅ **Good**: "I'm looking for wireless earbuds under $100"

This helps ShopBot filter out products outside your price range immediately.

### 3. Describe Your Use Case

✅ **Good**: "I need a laptop for video editing and graphic design"

This helps ShopBot prioritize relevant features (powerful processor, good graphics, large screen).

### 4. Mention Deal-Breakers

✅ **Good**: "I need waterproof headphones for swimming"

This ensures ShopBot only shows products that meet your essential requirements.

### 5. Ask Follow-Up Questions

Don't hesitate to ask for:
- More options
- Cheaper/more expensive alternatives
- Products with specific features
- Clarification about product details

**Examples:**
```
"Do you have anything with better battery life?"
"What's the difference between option 1 and option 2?"
"Show me more options in this price range"
```

### 6. Provide Feedback

If recommendations don't match your needs:
```
"These are too expensive"
"I need something more portable"
"I prefer a different brand"
```

ShopBot will adjust its recommendations based on your feedback.

---

## Troubleshooting

### ShopBot Isn't Responding

**Possible Causes:**
1. Internet connection issue
2. Server temporarily unavailable
3. Browser compatibility issue

**Solutions:**
1. Check your internet connection
2. Refresh the page (F5 or Cmd+R)
3. Try a different browser
4. Clear browser cache and cookies
5. Wait a few minutes and try again

### Recommendations Don't Match My Needs

**Solutions:**
1. Provide more specific information about your requirements
2. Mention your budget explicitly
3. Describe your use case in detail
4. Ask for different options
5. Specify features you need or don't want

### Can't See Product Images

**Solutions:**
1. Check your internet connection
2. Disable ad blockers temporarily
3. Allow images in browser settings
4. Refresh the page

### Conversation History Lost

**Note**: ShopBot maintains conversation history during your session using browser cookies. If you:
- Close the browser tab
- Clear cookies
- Use incognito/private mode

Your conversation history will be reset. This is by design for privacy.

### Prices Seem Incorrect

**Note**: Prices are converted from INR to USD using a standard exchange rate. Actual prices on Amazon may vary due to:
- Real-time exchange rate fluctuations
- Regional pricing differences
- Time-sensitive deals and promotions

Always verify the final price on the Amazon product page before purchasing.

---

## Privacy & Data

### What Information Does ShopBot Collect?

**During Your Session:**
- Your chat messages
- Product preferences you mention
- Conversation history (temporary)

**NOT Collected:**
- Personal identification information
- Payment information
- Browsing history outside ShopBot
- Email or phone number

### How Is My Data Used?

Your conversation data is used **only** to:
1. Generate personalized product recommendations
2. Maintain conversation context during your session
3. Improve recommendation accuracy

### Data Retention

- **Session Data**: Stored temporarily in your browser (cookies)
- **After Session**: Conversation history is **not** permanently stored
- **No Long-Term Storage**: Your preferences are not saved between sessions

### Privacy-by-Design

ShopBot follows privacy-by-design principles:
- Minimal data collection
- No unnecessary personal data storage
- Session-based processing only
- No data sharing with third parties

### Cookies

ShopBot uses a single session cookie to:
- Maintain conversation continuity
- Remember context across messages

You can clear this cookie anytime through your browser settings.

---

## FAQ

### General Questions

**Q: Is ShopBot free to use?**
A: Yes, ShopBot is completely free. You only pay for products you choose to purchase on Amazon.

**Q: Do I need to create an account?**
A: No, ShopBot works without registration or login.

**Q: Can I use ShopBot on mobile?**
A: Yes, ShopBot works on any device with a modern web browser.

**Q: Does ShopBot work in all countries?**
A: ShopBot currently uses Amazon India's product catalog. Availability may vary by region.

### Product Questions

**Q: Are the products real?**
A: Yes, all products are from Amazon's actual catalog with real prices and ratings.

**Q: Can I buy products directly through ShopBot?**
A: No, ShopBot provides recommendations and links. You complete purchases on Amazon.

**Q: How current is the product information?**
A: Product data is regularly updated, but prices and availability may change on Amazon.

**Q: Why don't I see all Amazon products?**
A: ShopBot focuses on popular, well-reviewed products to provide quality recommendations.

### Recommendation Questions

**Q: How does ShopBot choose recommendations?**
A: ShopBot uses a ranking algorithm that considers:
- Your stated preferences (budget, use case, features)
- Product ratings and review counts
- Keyword matching with your requirements
- Price-to-value ratio

**Q: Can I get recommendations without answering questions?**
A: ShopBot needs at least a product category and one preference (budget, use case, or features) to provide meaningful recommendations.

**Q: Why does ShopBot ask so many questions?**
A: Questions help ShopBot understand your needs and avoid showing irrelevant products. Typically, 2-5 questions are enough.

**Q: Can I skip questions?**
A: You can provide all information upfront to minimize questions:
```
"I need wireless headphones under $100 for gym workouts with good bass"
```

### Technical Questions

**Q: What browsers are supported?**
A: All modern browsers (Chrome, Firefox, Safari, Edge) from the last 2 years.

**Q: Why is ShopBot slow sometimes?**
A: Response time depends on:
- Internet connection speed
- Server load
- Complexity of your request

**Q: Can I use ShopBot offline?**
A: No, ShopBot requires an internet connection to access product data and AI services.

**Q: Is my conversation private?**
A: Yes, conversations are processed securely and not permanently stored.

### Shopping Questions

**Q: Does ShopBot guarantee the best price?**
A: ShopBot shows current prices from the database, but Amazon prices change frequently. Always verify on Amazon before purchasing.

**Q: Can ShopBot help with returns or customer service?**
A: No, for post-purchase support, contact Amazon directly.

**Q: Are product ratings reliable?**
A: Ratings shown are from Amazon's actual customer reviews.

**Q: Can I save my favorite products?**
A: Currently, ShopBot doesn't have a save feature. Copy product links to save them externally.

---

## Getting Help

### Need More Assistance?

If you encounter issues not covered in this manual:

1. **Refresh the page** and try again
2. **Check the Troubleshooting section** above
3. **Try a different browser** if problems persist
4. **Contact support** (if available in your deployment)

### Providing Feedback

Help us improve ShopBot:
- Report bugs or issues
- Suggest new features
- Share your experience

---

## Quick Reference Card

### Common Commands

| What You Want | What to Say |
|---------------|-------------|
| Start shopping | "I need [product]" |
| Set budget | "Under $X" or "Around $X" |
| Specify use case | "For [purpose]" |
| Request features | "With [feature]" |
| See more options | "Show me more" |
| Get cheaper options | "Something cheaper" |
| Get better quality | "Higher quality" |
| Ask about product | "Tell me about [product]" |
| Compare products | "What's the difference?" |
| Start over | "I want to look for something else" |

### Example Conversations

**Example 1: Quick Purchase**
```
You: "I need a phone charger under $20"
ShopBot: "What type of phone do you have?"
You: "iPhone"
ShopBot: [Shows 3 iPhone charger options with comparison]
```

**Example 2: Detailed Search**
```
You: "Looking for a laptop"
ShopBot: "What's your budget?"
You: "Around $1000"
ShopBot: "What will you use it for?"
You: "Gaming and streaming"
ShopBot: "Any specific requirements?"
You: "Good graphics and at least 16GB RAM"
ShopBot: [Shows gaming laptops with detailed comparison]
```

**Example 3: Gift Shopping**
```
You: "I need a gift for my dad"
ShopBot: "What are his interests?"
You: "He likes photography"
ShopBot: "What's your budget?"
You: "Up to $200"
ShopBot: [Shows camera accessories and photography gear]
```

---

## Appendix: Product Categories

ShopBot can help you find products in these categories:

### Electronics
- Computers & Accessories
- Mobile Phones & Accessories
- Cameras & Photography
- Audio & Video Equipment
- Home Theater & TV
- Wearable Technology
- Gaming Consoles & Accessories

### Home & Kitchen
- Large Appliances
- Small Appliances
- Kitchen & Dining
- Furniture
- Home Décor
- Bedding & Bath

### Sports & Outdoors
- Exercise & Fitness
- Outdoor Recreation
- Sports Equipment
- Camping & Hiking

### Office Products
- Office Electronics
- Office Supplies
- Furniture & Lighting

### Automotive
- Car Electronics
- Car Accessories
- Tools & Equipment

### Health & Personal Care
- Health Care
- Personal Care Appliances
- Wellness & Relaxation

### Books & Media
- Books
- Movies & TV
- Music
- Video Games

### Fashion
- Clothing
- Shoes
- Jewelry & Watches
- Bags & Luggage

---

**Version**: 1.0  
**Last Updated**: April 2026  
**For Technical Support**: See deployment-specific contact information

---

*Thank you for using ShopBot! Happy Shopping!* 🛍️
