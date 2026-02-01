# Hackathon Test Examples - 5 Key Regulations

## Test Cases for Your Geo-Compliance System

### ✅ **Should Flag as GEO-COMPLIANCE REQUIRED**

#### 1. EU Digital Services Act (DSA)
```
Title: Content moderation transparency system for EU users
Description: Implement transparent content flagging and user reporting mechanisms for European users, including algorithm transparency reports and illegal content removal procedures as required by EU DSA.
Expected: 🚨 GEO-SPECIFIC COMPLIANCE REQUIRED - EU DSA
```

#### 2. California Kids Act
```
Title: Age estimation system with privacy by default for minors  
Description: Feature estimates user age and applies highest privacy settings by default for users under 18, with data minimization for California users in compliance with the Age-Appropriate Design Code.
Expected: 🚨 GEO-SPECIFIC COMPLIANCE REQUIRED - CA Kids Act
```

#### 3. Florida Minor Protections
```
Title: Parental notification system for minor accounts
Description: Send notifications to verified parent accounts when Florida minors attempt to access restricted social media features, with parental consent requirements for account creation.
Expected: 🚨 GEO-SPECIFIC COMPLIANCE REQUIRED - FL Minor Protections
```

#### 4. Utah Social Media Regulation Act  
```
Title: Curfew-based login restrictions for Utah minors
Description: Automatically lock out user accounts from 10:30 PM to 6:30 AM for verified minors in Utah, with parental override capabilities and identity verification requirements.
Expected: 🚨 GEO-SPECIFIC COMPLIANCE REQUIRED - UT Social Media Act
```

#### 5. US NCMEC Reporting
```
Title: Automated child abuse content detection and reporting
Description: Implement automated scanning for child sexual abuse material (CSAM) with direct reporting to NCMEC as required by US federal law, including law enforcement notification protocols.
Expected: 🚨 GEO-SPECIFIC COMPLIANCE REQUIRED - US NCMEC
```

---

### ❌ **Should NOT Flag (Business Decisions)**

#### Business Testing Examples
```
Title: Geofences feature rollout in US for market testing
Description: Rolling out new video feature in US market first to test user engagement metrics before considering global expansion.
Expected: ✅ NO GEO-SPECIFIC COMPLIANCE DETECTED - Business Decision
```

```
Title: A/B testing recommendation algorithm in European markets
Description: Testing new recommendation algorithm performance in EU to optimize user retention and engagement metrics for revenue growth.
Expected: ✅ NO GEO-SPECIFIC COMPLIANCE DETECTED - Business Decision  
```

---

### ❓ **Should Flag for Manual Review (Unclear Intent)**

#### Ambiguous Cases
```
Title: Video filter feature available globally except South Korea
Description: New video filter available in all regions except South Korea due to regional considerations.
Expected: ❓ MANUAL REVIEW REQUIRED - Unclear if business or compliance driven
```

```
Title: Chat feature pilot program in California and Texas
Description: Limited rollout of new chat functionality in California and Texas markets for initial testing phase.
Expected: ❓ MANUAL REVIEW REQUIRED - Could be business testing or compliance-driven
```

---

## 🎯 **Testing Instructions**

1. **Go to your frontend**: http://localhost:8501
2. **Choose "Single Feature Analysis"**
3. **Copy/paste the examples above**
4. **Verify the system correctly identifies**:
   - ✅ Clear legal requirements (should flag)
   - ❌ Business decisions (should not flag)  
   - ❓ Ambiguous cases (should request manual review)

## 🏆 **Success Criteria**

Your system should achieve:
- **High Precision**: Only flags actual legal requirements
- **Clear Reasoning**: Explains WHY it flagged or didn't flag
- **Specific Regulation Detection**: Identifies which of the 5 laws apply
- **Audit Trail**: Provides evidence sources for decisions
- **Actionable Recommendations**: Tells compliance team what to do next

## 📊 **Expected Results Format**

For legal requirements:
```json
{
  "needs_geo_logic": true,
  "confidence": 0.90,
  "reasoning": "Strong regulatory compliance signals detected...",
  "applicable_regulations": [
    {
      "name": "EU Digital Services Act",
      "jurisdiction": "European Union",
      "relevance": "high"
    }
  ],
  "risk_assessment": "high",
  "evidence_sources": ["EU DSA regulation detection"],
  "recommended_actions": ["Implement geo-location detection", "Design compliance verification system"]
}
```
