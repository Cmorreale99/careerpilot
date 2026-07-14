---
source_file: "2nd brain/career artifacts/raw drive/Consensus hackathon_ The cryptosphere.pdf"
source_sha256: 231a80294f64f3990172eac33437436717a271613f84be569bfae91368b8df36
converter: pdfplumber 0.11.10
---

<!-- source page 1 -->

Welcome to the cryptosphere!
Introduction:
Due to all the moving parts, in the introduction we will explain how the app works before
getting into the business model, roadmap to launch, and future goals.
What is the learning hub?
When a user first downloads the app, they create an account (we leverage Suis zklogin for
security and scalability purposes). After the user logs in to their account, they are taken to
the learning hub. In the learning hub is a webpage that has 6 buttons, deposit, withdraw,
convert, log out, web3 discussion board, and cryptosphere. Once users complete the
designated quests in the learning hub (A page where users are given a series of quests to
complete which arms them with the basics of web3 and blockchain), they unlock access to
the web3 discussion board and cryptosphere. Users earn rewards such as SUI tokens, etc
from completing the initial quests in the learning hub, and for positive contributions to the
web3 discussion board. These tokens can be converted to USD and cashed out, or they can
be used in the cryptosphere.
Possible flaws: People buying a shitload of SUI to get more voting power, then using that
voting power to brigade.
Possible solution: Remove voting power
What is the web3 discussion board?
The web3 discussion board is the idea we used at the last hackathon, users earn rewards
for positive contributions, factoids with lots of reposts and comments, etc. Suis vote
delegation feature makes it easy to penalize bad actors, they have less voting power while
positive contributors have more. Thus, top contributors have the most control over what
content is featured at the top of the page while bad actors who post and comment get
pushed down to the bottom, and do not earn rewards. In fact, they lose tokens. If a user
makes a post that gets them flagged as a bad actor AND they have below a certain amount
of tokens in their account, they lose access to the cryptosphere until they get over 1000 SUI
in their account. These bad actors can only regain that access by either spending a lot of
$$$, depositing to their accounts, and then converting to SUI, or rebuilding their reputation
on the web3 discussion board via lots of good posts (very difficult to do). So basically, don't
fuck around and troll or you will pay the price.
What is the cryptosphere?
The cryptosphere is a metaverse (Use live NFT from unique for 4k bounty), a virtual world
that users can enter with the click of a button. The cryptosphere has it all, an NFT
marketplace, video games, a virtual casino, etc. The crypto earned from the learning hub is
the currency used in the cryptosphere. Users create their interactive NFT avatars, and
they walk around, with various minigames and a shop that you can cash winnings in at the
NFT marketplace.

<!-- source page 2 -->

NFT marketplace: Will have several additions in the shop that can be added to your
avatar.
Cryptosphere gaming: Web3 Jeopardy! Users can enter a game with 2 other
contestants for 100 SUI tokens. Web3 Jeopardy is extremely similar to regular jeopardy, but
all the categories are crypto or web3 related. Factoids used for the game are taken from the
web3 discussion board (randomly selected among the top 10% hourly posts…. good luck
trying to dig through everything to cheat). Web3 Jeopardy uses a similar skill matchmaking
algorithm and anti-cheat detection to keep the game fair. Even if someone figures out a way
to successfully cheat, the similar skill matchmaking algorithm (designed to ensure a 33%
chance of getting 1st, 33% chance of getting 2nd, 33% chance of getting 3rd) will simply
match them up with people of a similar elo (which will be other cheaters). The prize
distribution is as follows:
1st place: 150 SUI tokens
2nd place: 110 SUI tokens
3rd place: 0 SUI tokens
Note: The EV for playing this game is: 150 * .33 + 110 * .33 + 0 * .33 = -14.2 SUI tokens, so
the house always wins, just like in a regular casino. This is used to further build the pool to
reward users for quest completion. The best part is, people who play this game will be
winning SUI tokens 66% of the time. So there are going to be a lot of suckers laughing to
themselves about how they are winners who are robbing the house blind while getting
royally fucked over by the house. The house ALWAYS wins.
Other, easier to program ideas such as flappy bird
Retro games
For this hackathon: to win 4k bounty
To simplify things, we will build a simple game using Uniques multi
resource NFTs, which can integrate any file, image, video, audio, etc w/o
need for complex smart contracts.
For demonstration purposes, we will have a welcome to web3 jeopardy
screen, then jeopardy game board will be 3 categories and a 3x3 board.
The questions and answers will be coded into the game. There will be 3
podiums, with an avatar of 3 people and their current balance below. At
the end of the game, prizes will be awarded based on who got 1st, 2nd,
and 3rd place.

<!-- source page 3 -->

Use the unique SDK for dynamic NFTs, this will be used to create this
interactive game.
Backup plan if this is too complicated: you only need to implement
advanced unique NFTs in a web3 game app w/ unique network, the
game itself can be something really simple like tic tac toe. We could just
scrap this whole idea and do that instead, and then reward the winner
with a special advanced NFT collection. That would satisfy the criteria.
Online casino (future work)
Priorities for this hackathon
#1: Implement SUI: Get the learning hub set up with the web3
discussion board. This satisfies our social media web3 learning idea, if
we don’t get any further than this no big deal, monetize via
advertisements and staking pool. Also implement SUIs zklogin. This is a
MUST as this will be funding our flights. Personally, I dont think this will
be enough to win on its own UNLESS we have a bulletproof business
model w/ a practical roadmap including how we plan to fund the startup
for launch and a very strong future work section.
#2: Go after the polkadot 4k bounty: To satisfy this bounty, we must
implement advanced unique NFTs in a web3 game app w/ unique
network. We don’t need to nor will we be able to do everything
mentioned in this document, so we should decide as a group and
choose one of the below ideas.
● High risk high reward: The cryptosphere gaming metaverse:
Seems somewhat complex to actually program, but lots of future
earning potential and has a good chance of winning big if we pull it
off. Start by prompting user to create avatar, then have video
demonstration of the avatar walking around, jumping, etc in the
world.
● High risk high reward: Web3 Jeopardy as an alternative (or along
with if we somehow have the time) to the cryptosphere metaverse
idea, this offers high reward potential because the SUI tokens won
by the house is a reliable source of revenue AND is a means

<!-- source page 4 -->

where users both are actively learning about Web3 as well as
deriving entertainment from doing so.
● Lower risk lower reward: Tic tac toe idea, make the interactive tic
tac toe board using multi resource and dynamic NFTs. For
economic purposes, charge a certain amount of SUI to enter and
rig it so the house always wins. Would also need to create an NFT
marketplace for this (again using unique network), which seems
relatively simple to do.
#3 Go after the 2k polkadot bounty: The prompt is to build an AI agent
w/ Phala and OpenAI. This could potentially be linked with the Web3
discussion board, where users can spend tokens to access an AI agent
that is designed to help users make factual and informative posts about
web3.
