# NOVA Kutty WhatsApp Bot Lock

## WhatsApp Bot Components

1. `novakutty-dragon-brain`
   - Role: WhatsApp bot brain / reply thinking layer
   - Handles message understanding, response planning, and NOVA/DRAGON style routing.

2. `novakutty-whatsapp-approval`
   - Role: Approval gate
   - Rule: Bot must not send risky/important actions without Aslam approval.

## Safety Rule

WhatsApp bot flow:

receive message
→ understand
→ think with novakutty-dragon-brain
→ pass through novakutty-whatsapp-approval
→ ask Aslam approval if needed
→ send only approved reply
→ log action

## Owner

Creator / controller: Aslam  
Project: Universal Dragon  
Stable brain: NOVA  
Interface layer: EVE  
WhatsApp layer: NOVA Kutty
