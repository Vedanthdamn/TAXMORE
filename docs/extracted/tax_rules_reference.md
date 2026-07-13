# Tax rules reference (FY 2025-26)

Extracted from `docs/source-pdfs/income_tax_act_1961_relevant_section.pdf` (cited as "1961 Act") and
`docs/source-pdfs/finance_act_2025_slabs_circular.pdf` (cited as "2025 Act" - its section numbering
follows the new Income-tax Act, 2025, not the 1961 Act; see Unresolved section at the bottom).

Section numbers in the table below use the popularly known 1961 Act numbering (80C, 24(b), 87A, etc.)
since that is how these deductions are commonly referred to. Where the 2025 Act text was the source for
a figure, its corresponding section number is noted in Eligibility notes.

| Section number | Section name | Deduction limit | Old regime allowed? | New regime allowed? | Formula/logic | Eligibility notes |
|---|---|---|---|---|---|---|
| Standard deduction (s.16(ia), 1961 Act; s.19(1) Table Sl.2, 2025 Act) | Standard deduction from salary income | Rs. 50,000 (old regime) / Rs. 75,000 (new regime) | Yes | Yes | Flat deduction = lesser of the stated amount or actual salary | Only the employment-tax deduction (s.19(1) Table Sl.1) is excluded under the new regime per s.202(2)(a)(iv) of the 2025 Act; the standard deduction line item itself is not excluded |
| 80C | Life insurance premia, PF, ELSS, tuition fees, home-loan principal, etc. | Rs. 1,50,000 aggregate | Yes | No | Sum of qualifying payments, capped at Rs. 1,50,000 | Combined ceiling of Rs. 1,50,000 applies across 80C + 80CCC + 80CCD(1) (s.80CCE, 1961 Act). Excluded under new regime as part of Chapter VIII per s.202(2)(a)(xii), 2025 Act |
| 80CCC | Contribution to certain pension funds (LIC/insurer annuity plans) | Rs. 1,50,000 | Yes | No | Full amount deposited, capped at Rs. 1,50,000 | Shares the combined Rs. 1,50,000 ceiling with 80C/80CCD(1) via s.80CCE |
| 80CCD(1) | Employee's own contribution to NPS/Central Govt pension scheme | 10% of salary (employees) or 20% of gross total income (others) | Yes | No | min(actual contribution, 10% of salary or 20% of GTI) | Forms part of the combined Rs. 1,50,000 ceiling under s.80CCE along with 80C and 80CCC |
| 80CCD(1B) | Additional self-contribution to NPS | Rs. 50,000 | Yes | No | Full amount deposited, capped at Rs. 50,000, over and above the 80C/80CCD(1) ceiling | Not allowed under new regime - not among the carve-outs (s.124(1)/(2), 125(2), 146) listed in s.202(2)(a)(xii) of the 2025 Act |
| 80CCD(2) | Employer's contribution to employee's NPS account | 10% of salary (private employer, 1961 Act text); 14% of salary (Central/State Govt employer, and 14% for any employer under new regime) per s.124(1)-(2), 2025 Act | Yes | Yes | Deduction = employer's actual contribution, capped at the applicable % of salary | The only Chapter VIII deduction explicitly carved out as allowed under the new regime (s.202(2)(a)(xii) excludes it from the general Chapter VIII disallowance). The 1961 Act text read does not show a 14%-for-government-employer distinction - see Unresolved |
| 24(b) | Interest on borrowed capital for house property | Rs. 2,00,000 (self-occupied, construction completed within 5 years); Rs. 30,000 (self-occupied, not completed within 5 years); no statutory cap shown for let-out property | Yes | Partial | Interest payable on capital borrowed for acquisition/construction/repair, subject to the self-occupied caps above | Under the new regime, the deduction is disallowed only for self-occupied properties (s.202(2)(a)(v), 2025 Act, referencing s.22(1)(b) for properties under s.21(6)); interest on a let-out property is not in that exclusion list |
| 87A | Rebate of income-tax for resident individuals | Rs. 12,500 (old regime, income up to Rs. 5,00,000); Rs. 60,000 (new regime, income up to Rs. 12,00,000), with marginal relief above that | Yes | Yes (different limits) | Old: 100% of tax or Rs. 12,500, whichever less, if total income <= Rs. 5,00,000. New: 100% of tax or Rs. 60,000, whichever less, if total income <= Rs. 12,00,000; above that, marginal relief caps the rebate so incremental tax never exceeds incremental income over Rs. 12,00,000 | See `tax_slabs_fy2025_26.json` for the full marginal relief formula |
| 80D | Health insurance premia / preventive check-ups / medical expenditure | Rs. 25,000 (self+family, non-senior); Rs. 50,000 (self+family, senior citizen); Rs. 25,000 (parents, non-senior); Rs. 50,000 (parents, senior citizen); preventive check-up sub-limit Rs. 5,000 within the applicable cap | Yes | No | Aggregate of qualifying premiums/expenditure, capped per category above | Medical-expenditure limb (as opposed to insurance premium) only applies where the covered person is a senior citizen with no insurance in force |
| 80DD | Maintenance/medical treatment of a dependant with disability | Rs. 75,000 (disability); Rs. 1,25,000 (severe disability) | Yes | No | Flat deduction regardless of actual expenditure, subject to a medical authority certificate | Dependant must not have claimed a deduction under 80U for the same year |
| 80DDB | Medical treatment for specified diseases/ailments | Rs. 40,000 (general); Rs. 1,00,000 (senior citizen) | Yes | No | Amount actually paid or the cap, whichever is less, reduced by any insurance/employer reimbursement | Requires a prescription from a specialist as prescribed |
| 80E | Interest on loan for higher education | No cap | Yes | No | Full interest amount paid, no ceiling | Allowed for the initial assessment year plus 7 succeeding years, or until the interest is paid in full, whichever is earlier; loan must be for the assessee's or a relative's higher education |
| 80EE | Interest on loan for first residential house property | Rs. 50,000 | Yes | No | Full interest paid, capped at Rs. 50,000 | Legacy provision - only applies to loans sanctioned between 1 Apr 2016 and 31 Mar 2017, loan <= Rs. 35 lakh, property value <= Rs. 50 lakh, and assessee owned no other residential property on the sanction date. Not applicable to loans taken in FY2025-26 |
| 80G | Donations to specified funds/charitable institutions | 50% or 100% of donation, some categories subject to a qualifying limit of 10% of adjusted gross total income | Yes | No | Varies by donee category | Full donee-category breakdown not extracted here - see s.80G of the 1961 Act for the complete list |
| 80GG | Rent paid, where HRA is not received | Least of: (rent paid - 10% of total income), Rs. 5,000/month, or 25% of total income | Yes | No | min(rent - 10% of TI, Rs. 60,000/year, 25% of TI) | Only available to assessees who do not receive HRA under s.10(13A) and who (with spouse/minor child/HUF) do not own residential accommodation at the place of work |
| 80GGA | Donations for scientific research or rural development | Full amount of qualifying donation | Yes | No | Full amount, no cap stated | Not available to assessees who have income from business or profession |
| 80GGC | Contributions to political parties/electoral trusts | Full amount of contribution | Yes | No | Full amount, no cap | Cash contributions are not eligible |
| 80TTA | Interest on savings account deposits | Rs. 10,000 | Yes | No | Actual interest income or Rs. 10,000, whichever is less | Not available to senior citizens (they use 80TTB instead); does not cover time/fixed deposits |
| 80TTB | Interest on deposits (senior citizens) | Rs. 50,000 | Yes | No | Actual interest income or Rs. 50,000, whichever is less | Covers both savings and time deposits, for individuals aged 60+; supersedes 80TTA for senior citizens |
| 80U | Deduction for a person with disability | Rs. 75,000 (disability); Rs. 1,25,000 (severe disability) | Yes | No | Flat deduction, requires medical authority certification | Claimed by the disabled individual themselves (contrast with 80DD, claimed by a family member on behalf of a dependant) |

## Unresolved / not found in source PDFs

- **Old-regime slab table** for individuals is not present in either PDF. The 1961 Act text never carries
  rate schedules (those live in the annual Finance Act's First Schedule); `finance_act_2025_slabs_circular.pdf`
  only contains the new-regime table (section 202). Do not assume the commonly cited 2.5L/5L/10L old-regime
  brackets without an authoritative source.
- **Health and Education Cess rate** is not stated in either PDF.
- **Surcharge** rates/thresholds for individuals are not present in either PDF.
- **80CCD(2) government-employer rate discrepancy**: `income_tax_act_1961_relevant_section.pdf`'s text of
  section 80CCD(2) states a flat 10% of salary with no separate rate for Government employers, while
  `finance_act_2025_slabs_circular.pdf`'s section 124(1) explicitly splits this into 14% (Central/State
  Government employer) and 10% (other employers), further raised to 14% for all employers under the new
  regime. This is a genuine discrepancy between the two source documents, not a transcription error -
  flagging rather than picking one.
- **80G donee-category percentages/limits** were not broken out in detail (the section has many
  sub-categories with different rates and qualifying limits); only a summary was extracted.
- The identity/scope of `finance_act_2025_slabs_circular.pdf` is itself ambiguous: its content and section
  numbering (Chapter/section 199-209, footnotes referencing "Finance Act, 2026, w.e.f. 1-4-2026") indicate
  it is text from the new Income-tax Act, 2025, rather than a slab-only circular. Its applicability to
  FY2025-26 specifically (versus a later tax year) should be verified before this document is treated as
  authoritative for FY2025-26 in user-facing product copy.
- **HRA exemption formula (Rule 2A)** is not covered by this document - see `docs/extracted/hra_cities.json`,
  which was populated from general knowledge (not these PDFs) at the user's direction and is explicitly
  flagged there as unverified.
