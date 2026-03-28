Skip to content
BerriAI
litellm
Repository navigation
Code
Issues
948
(948)
Pull requests
1.1k
(1.1k)
Agents
Discussions
Actions
Projects
Security
Insights
[Security]: litellm PyPI package (v1.82.7 + v1.82.8) compromised — full timeline and status #24518
Open
Open
[Security]: litellm PyPI package (v1.82.7 + v1.82.8) compromised — full timeline and status
#24518
@isfinne
Description
isfinne
opened 9 hours ago · edited by krrish-berri-2
[LITELLM TEAM UPDATES]

Compromised packages have been deleted (v1.82.7, v1.82.8)
Compromise came from trivvy security scan dependency
All maintainer accounts have been rotated (new maintainer accounts: @krrish-berri-2 , @ishaan-berri)
Proxy Docker image users were not impacted, all dependencies are pinned on requirements.txt
No litellm releases will be out until we have scanned our chain and make sure it's safe
Next Steps

Review all berriai repo's for impact
Scan circle ci builds to understand blast radius, and mitigate it
We've engaged Google's mandiant.security team, and are actively working on this with them
We are actively investigating this issue. Please reach out to us on support@berri.ai, if you have any questions / concerns.

Summary
The litellm PyPI package was compromised by an attacker who gained access to the maintainer's PyPI account. Malicious versions were published that steal credentials and exfiltrate them to an attacker-controlled server.

Original detailed analysis: #24512

Hacker News discussion: https://news.ycombinator.com/item?id=47501729

What happened
The maintainer's PyPI account (krrishdholakia) appears to have been hijacked by an attacker (teampcp)
The attacker published malicious versions to PyPI that were never released through the official GitHub CI/CD
GitHub releases only go up to v1.82.6.dev1 — versions 1.82.7 and 1.82.8 on PyPI were uploaded directly by the attacker
Affected versions
Version Method Trigger
1.82.7 Payload embedded in litellm/proxy/proxy_server.py Triggered on import litellm.proxy
1.82.8 Added litellm_init.pth (34,628 bytes) + payload in proxy_server.py Any Python startup — no import needed
Other versions may also be affected and should be audited.

What the malicious code does
Collects: SSH keys, environment variables (API keys, secrets), AWS/GCP/Azure/K8s credentials, crypto wallets, database passwords, SSL private keys, shell history, CI/CD configs
Encrypts: AES-256-CBC + RSA-4096 (hardcoded public key)
Exfiltrates: curl POST to https://models.litellm.cloud/
The exfiltration domain litellm.cloud (NOT the official litellm.ai) was registered on 2026-03-23 via Spaceship, Inc. — just hours before the malicious packages appeared.

Current status
PyPI: The entire litellm package has been suspended/removed. All versions currently return "No matching distribution found." We reported the malware to PyPI via the official "Report malware" form.
GitHub Issue [Security]: CRITICAL: Malicious litellm_init.pth in litellm 1.82.8 — credential stealer #24512: Contains the original detailed technical analysis (currently closed by the attacker's spam — see below).
Attacker behavior: The attacker appears to be publishing hundreds of spam comments to suppress discussion. If this continues, we recommend moderating via the Hacker News thread linked above.
Recommendations for affected users
Check if litellm_init.pth exists in your site-packages/ directory
Rotate ALL credentials that were present as environment variables or config files on any system where litellm 1.82.7+ was installed
Pin dependencies to exact versions and verify against GitHub releases
Monitor for unauthorized access using any potentially leaked credentials
References
Original analysis: [Security]: CRITICAL: Malicious litellm_init.pth in litellm 1.82.8 — credential stealer #24512
Hacker News: https://news.ycombinator.com/item?id=47501729
Attacker's exfil domain WHOIS: registered 2026-03-23, Spaceship Inc., privacy-protected
litellm_init.pth SHA256: ceNa7wMJnNHy1kRnNCcwJaFjWX3pORLfMh7xGL8TUjg
Activity

github-actions
added
llm translation
9 hours ago

krrishdholakia
mentioned this 9 hours ago
[Security]: CRITICAL: Malicious litellm_init.pth in litellm 1.82.8 — credential stealer #24512

krrishdholakia
pinned this issue 9 hours ago
krrishdholakia
krrishdholakia commented 9 hours ago
krrishdholakia
9 hours ago
Contributor
Pypi has put the project in quarantine. this should block additional downloads.

thenoblet
thenoblet commented 9 hours ago
thenoblet
9 hours ago
Pypi has put the project in quarantine. this should block additional downloads.

Our entire deployment has failed due to this issue. Pypi quarantined it, and I am just finding out. Such a bummer!!

DanielRuf
DanielRuf commented 9 hours ago
DanielRuf
9 hours ago · edited by DanielRuf
This was probably caused by the compromised trivy project:

https://github.com/search?q=repo%3ABerriAI%2Flitellm%20trivy&type=code
https://ramimac.me/trivy-teampcp/#phase-09

litellm/ci_cd/security_scans.sh

Line 16 in 9343aee

echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
The full timeline contains more details.

m-rossi
mentioned this 9 hours ago
litellm >=1.82.7 got compromised notebook-intelligence/notebook-intelligence#125
akx
akx commented 9 hours ago
akx
9 hours ago
The maintainer's PyPI account (krrishdholakia) appears to have been hijacked by an attacker (teampcp)

Note that it's not just PyPI... See e.g. krrishdholakia/blockchain@556f2db (unrelated repo) (and other recent activity).

DanielRuf
DanielRuf commented 9 hours ago
DanielRuf
9 hours ago · edited by DanielRuf
Yes, the trivy project contained a credential stealer and the threat actors used PATs and other secrets extracted via CI / CD.

This means full rotation after cleanup for all involved secrets and connected services (PyPi etc).

dkindlund
dkindlund commented 9 hours ago
dkindlund
9 hours ago
Contributor
The Attack Chain: Trivy → LiteLLM PyPI

Based on the ramimac writeup and issue #24518:

1. March 1: Aqua Security (Trivy's maintainer) suffered an initial breach
2. Incomplete credential rotation left tokens available to the attacker (TeamPCP)
3. TeamPCP compromised Trivy — poisoned v0.69.4-v0.69.6, force-pushed all 76+ trivy-action tags, and pushed malicious Docker images directly to Docker Hub
4. March 23: Attacker registered litellm.cloud domain (exfiltration target)
5. March 24 ~08:30 UTC: Published malicious litellm==1.82.7 and 1.82.8 to PyPI using the compromised maintainer account krrishdholakia

The connection: the Trivy compromise likely gave the attacker access to the LiteLLM maintainer's PyPI credentials (either harvested from CI secrets via the compromised Trivy runs, or through the broader credential-stealing payload).

GitHub Source Code: NOT Compromised

- No malicious code in any GitHub tag from v1.82.3-stable through v1.82.6.rc.2
- No v1.82.7 or v1.82.8 tags exist on GitHub — the attacker published directly to PyPI
- The base64 and subprocess usages in proxy_server.py across all tagged versions are legitimate (config handling, callbacks)
- No .pth files, no litellm.cloud references, no exec(base64.b64decode(...)) patterns in the source
- The simple_pypi_publish.yml workflow was last modified July 2025 — not tampered with
- Last legitimate CI-published version was March 13

LiteLLM's Trivy Usage — Potential Exposure Vector

LiteLLM's ci_cd/security_scans.sh installs Trivy via apt from aquasecurity.github.io/trivy-repo/deb without version pinning — it pulls whatever the latest version is. If a CI run occurred during the Trivy compromise window, it would have installed the poisoned Trivy, which could have exfiltrated CI secrets including the PYPI_PUBLISH_PASSWORD.

Yannholo
mentioned this 9 hours ago
litellm dependency breaks all installs — package quarantined on PyPI after supply chain attack google/adk-python#4981

CalebCourier
mentioned this in 3 issues 9 hours ago
Fresh install broken: litellm removed from PyPI causes ResolutionImpossible guardrails-ai/guardrails-ai#5
URGENT - LiteLLM 1.82.7+ Contains an Exfiltration Vulnerability guardrails-ai/guardrails#1445
URGENT - LiteLLM 1.82.7+ Contains an Exfiltration Vulnerability guardrails-ai/guardrails-api#111
hdnh2006
hdnh2006 commented 9 hours ago
hdnh2006
9 hours ago
Pypi has put the project in quarantine. this should block additional downloads.

Your account is compromised dude:

Image
98 remaining items
krrish-berri-2
krrish-berri-2 commented 3 hours ago
krrish-berri-2
3 hours ago
Contributor
@seljak00vac - that commit seems like it occurred during the time of attack.

We've since deleted all github PAT's and removed repo access for those accounts.

seddy-aisi
added a commit that references this issue 3 hours ago
Explicitly avoid compromised LiteLLM versions

fd60893
Manouchehri
Manouchehri commented 3 hours ago
Manouchehri
3 hours ago
Contributor
#23383 (comment)

The unit tests and code quality of LiteLLM has been fundamentally broken for 1-2 years. Shipping new features has been the priority above everything else, including existing features (which have been constantly breaking/regressing) and security.

I'm disappointed this happened, but I can't say I'm surprised. That's why we distanced and disconnected our resources from LiteLLM ~2 weeks ago.

apthagowda97
apthagowda97 commented 3 hours ago
apthagowda97
3 hours ago
Trivy attack happened on 19th March ( correct me if i am wrong ) and you guys were using it for CI. Just curious why there was no action?

As a security measure both Krrish and I rotated our github accounts.

ishaan-berri
ishaan-berri commented 3 hours ago
ishaan-berri
3 hours ago
Contributor
@apthagowda97, that's a fair point. We're investigating how we can do a better job here. We will post updates by end of week on how we could have done better here

me-her
mentioned this 2 hours ago
[Security] litellm dependency exposes ADK users to supply chain attack (PYSEC-2026-2) google/adk-python#4986

aig-
mentioned this 2 hours ago
[Security]: litellm PyPI package (v1.82.7 + v1.82.8) compromised! getsentry/sentry-python#5856

alan-cooney-dsit
added a commit that references this issue 2 hours ago
Explicitly avoid compromised LiteLLM versions (#786)

Verified
523edb1

nsphung
mentioned this in 2 pull requests 1 hour ago
Update litellm[proxy] version constraints to avoid compromised versions. microsoft/agent-lightning#507
Modify litellm dependency constraints ag2ai/ag2#2512

KyubumShin
mentioned this 1 hour ago
[Security Advisory] litellm 1.82.8 supply chain compromise — credential stealer affects LiteLLM proxy users Yeachan-Heo/oh-my-claudecode#1864

MaxMLang
added a commit that references this issue 44 minutes ago
fix: pin litellm <1.82.7 to block compromised PyPI releases

261ef94

waynesun09
added a commit that references this issue 22 minutes ago
security: lock litellm version to exclude compromised releases

cae59e3

waynesun09
mentioned this 21 minutes ago
security: lock litellm version to exclude compromised releases calebevans/cordon#23

hoelzl
added a commit that references this issue 18 minutes ago
Remove litellm dependency, replace with openai SDK

1abab93
detroittommy879
Add a comment
new Comment
Markdown input: edit mode selected.
Write
Preview
Use Markdown to format your comment
Remember, contributions to this repository should follow its contributing guidelines and security policy.
Metadata
Assignees
No one assigned
Labels
llm translation
Type
No type
Projects
No projects
Milestone
No milestone
Relationships
None yet
Development
No branches or pull requests
NotificationsCustomize
You're not receiving notifications from this thread.

Participants
@akx
@dkindlund
@JoseBarrios
@DanielRuf
@pwilkin
Issue actions
Footer
© 2026 GitHub, Inc.
Footer navigation
Terms
Privacy
Security
Status
Community
Docs
Contact
Manage cookies
Do not share my personal information
