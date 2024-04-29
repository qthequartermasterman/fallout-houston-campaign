# Fallout: Houston Outline

## Quest Diagram
    
``` mermaid
flowchart LR
    subgraph prologue["Prologue: Dawn of Tranquility"]
        P1[Main Quest: Lunar Conspiracy Unveiled]
        P_rest[Other vignettes from _Dawn of Tranquility_ are presented throughout the rest of the campaign as narrative devices.]
    end
    subgraph act1["Act 1: Rising Tensions"]
        A1[Main Quest: Lost in the Bayou];
        A2[Main Quest: Diplomatic Relations];
        A3[Main Quest: Pirate's Plunder];
        A4[Main Quest: Lone Star Ambitions];
        A5[Main Quest: Visions of Betrayal];
        A6[Main Quest: Unveiling the Conspiracy];
        A1 --> A2;
        A2 --> A3;
        A2 --> A4;
        A3 --> A5;
        A4 --> A5;
        A5 --> A6;
    end
    subgraph act2[Act 2: The Faction Game]
        B1[Main Quest: Summit's Shadow]
        subgraph pirate["Galveston Pirates"]
            B2pirate[Main Quest: Sunken Treasure]
            B3pirate[Main Quest: You and What Army?]
            B4pirate[Main Quest: Rallying the Reavers]
            B5pirate[Main Quest: Tides of Conquest]
            B6pirate[Main Quest: The Pirate King] 
            
            B2pirate --> B3pirate --> B5pirate --> B6pirate;
            B2pirate--> B4pirate --> B5pirate;
        end
        subgraph oilbaron["Oil Barons"]
            B2oilbaron
        end
        subgraph lsr["Lone Star Republic"]
            B2lsr[Main Quest: Ghosts of the Costa Concordia]
            B3lsr[Main Quest: Black Gold Machinations]
            B4lsr[Main Quest: Fortifying the Frontier]
            B5lsr[Main Quest: The Enemy of my Enemy is not my Friend]
            
            B2lsr --> B3lsr --> B4lsr --> B5lsr;
        end
        subgraph enclave["Enclave"]
            B2enclave
        end
        
        B1 --> B2pirate;
        B1 --> B2lsr;
        B1 --> B2oilbaron;
        B1 --> B2enclave;
    end
    subgraph act3["Act 3: The Battle for the Spaceport"]
    end
    prologue --> act1 --> act2 --> act3;
```

## Prologue: Dawn of Tranquility

### Plot Beats:

- Player wakes up in a unique and unfamiliar environment: a pristine, advanced Vault-Tec facility located on the Moon. This Vault serves as a highly secretive lunar mining operation, operated in partnership with the US government to extract valuable resources. 
- As the player acclimates to the surroundings and learns about their role as a Vault-Tec security officer, they are thrust into an unexpected conflict, when the Chinese launch a covert attack on the lunar facility, assisted by traitors within the player's squadron.

## Act 1: Rising Tensions
*Main Article [Act 1: Rising Tensions](./Act1/index.md)*

### Plot Beats:

- Introduction to the Gulf Coast Wasteland: The player begins six months after the prologue, emerging into the post-apocalyptic Gulf Coast Wasteland. They start with their chosen background, which can be a former Lone Star Republic soldier, a Bayou Brotherhood member, a Galveston Pirate, or any other option. The Lone Star Republic has already established relations with the Spaceport Survivors.
- Meeting the Factions: The player encounters various factions in the region, including the Lone Star Republic, Galveston Pirates, Bayou Brotherhood, and Oil and Energy Barons. Each faction offers quests and opportunities for the player to align themselves or remain independent.
- Character Background Quest: Depending on the player's chosen background, they engage in a quest related to their past, giving them a sense of identity and purpose. For example, a Lone Star Republic soldier may investigate a missing squad member's connection to the spaceport.
- The Enclave Connection: The player begins experiencing intermittent visions of their great-great-grandfather's campaign in the Battle of the Sea of Tranquility. These visions reveal an Enclave conspiracy within the USSA and Space Force. The player's visions should mirror their own choices and interactions in the present, drawing parallels between past and present actions.
- Spaceport Survivors' Mysterious Agenda: The Spaceport Survivors appear as enigmatic figures with a hidden agenda. They maintain that their manned space mission is for the greater good but reveal little about their true intentions. The player learns that there are internal divisions within the Spaceport Survivors.
- Uncovering the Enclave Conspiracy: Through quests and interactions with various factions, the player starts uncovering clues about the Enclave's presence within the Spaceport Survivors. It becomes clear that the Enclave wants to gain control of the upcoming space mission for their own nefarious purposes.

### Act 1 Climax:

The first act reaches its climax when the player discovers concrete evidence of the Enclave's infiltration within the Spaceport Survivors. This revelation threatens not only the launch but also the stability of the entire region. The player must decide whether to confront the Enclave immediately or gather more information.

## Act 2: The Faction Game
*Main Article [Act 2: The Faction Game](./Act2/index.md)*

### Plot Beats:

- Faction Questlines: The player delves deeper into the conflicts and interests of the major factions by embarking on faction-specific questlines. These quests allow the player to build relationships, uncover faction secrets, and make significant choices that affect the story.
- Balancing Act: The player's interactions with factions have consequences. Depending on their choices, they may gain allies and enemies among the major and minor factions. The player can align with one faction or play different factions against each other, strategically advancing their goals.
- Enclave Threat Grows: The Enclave's presence becomes more pronounced as the player investigates further. The Enclave is willing to resort to drastic measures to gain control of the space mission, posing a significant threat to the Gulf Coast Wasteland.
- Character Growth: The player's character evolves based on their chosen background, actions, and affiliations. Their decisions impact their skills, abilities, and relationships with NPCs.
- Recurring Visions: The player continues to experience visions of their great-great-grandfather's campaign, with the parallel between past and present growing stronger. These visions provide insights into the Enclave's tactics and motives, helping the player strategize.
- Revealing Secrets: Through quests, exploration, and dialogue, the player gradually unveils the Spaceport Survivors' true objectives and the Enclave's plan to hijack the space mission. The player must gather allies and resources for the impending confrontation.
### Act 2 Climax:

The player, along with their chosen faction, discovers that the Enclave has begun executing their plan. They must decide whether to confront the Enclave directly, attempt to negotiate, or sabotage their plans. The fate of the Gulf Coast Wasteland hangs in the balance.

## Act 3: The Battle for the Spaceport
*Main Article [Act 3: The Final Showdown](./Act3/index.md)*

### Plot Beats:

- Preparing for the Launch: As the launch date for the manned space mission approaches, tension in the Gulf Coast Wasteland escalates. The player's actions and alliances determine the resources they have at their disposal.
- Alliances and Betrayals: Faction relationships reach a breaking point. The player must choose allies wisely, as some factions may betray them if it serves their interests. The Lone Star Republic, Galveston Pirates, Bayou Brotherhood, and Oil and Energy Barons all have a stake in the outcome.
- Confronting the Enclave: The player confronts the Enclave within the Spaceport Survivors, leading to a climactic battle within the spaceport's hidden chambers. The Enclave's plan to seize control of the space mission must be thwarted.
- Spaceport Standoff: The final act culminates in a standoff at the spaceport. The player, along with their chosen allies, faces off against the Enclave forces and Spaceport Survivors loyal to the conspiracy. The fate of the manned space mission hangs in the balance.
- Player's Choice: The player's decisions throughout the game determine the outcome. They can choose to launch the mission with the Spaceport Survivors, allowing humanity to take another step toward space exploration, or they can sabotage the launch to prevent the Enclave from gaining access to the orbital station.
- Resolution: The game concludes with an epilogue that reflects the player's choices and their impact on the Gulf Coast Wasteland. The fate of the factions, the player character, and the region's future are revealed based on the player's actions.

### Act 3 Climax:

The player faces a final choice: prioritize stopping the Enclave and securing the missile base or ensuring the safe launch of the historic rocket. The fate of the Gulf Coast Wasteland, and potentially the world beyond, depends on