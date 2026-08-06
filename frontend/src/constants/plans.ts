/**
 * Central product configuration for the premium paywall.
 * Prices live ONLY here — never hardcode them in the UI. The surrounding
 * words (currency period, "equals", trial length) come from i18n so the
 * numbers stay in a single source of truth.
 *
 * NOTE: purchases are placeholders in this step (no StoreKit / Play Billing yet).
 */
export type PlanId = "yearly_individual" | "family" | "lite" | "monthly";
export type PlanCta = "trial" | "unlock";

export type PlanOffer = {
  id: PlanId;
  /** i18n key for the plan title */
  titleKey: string;
  /** numeric price string in the app's display format (e.g. "110,99") */
  price: string;
  /** equivalent per-month price (only for yearly plans) */
  perMonth?: string;
  currency: string;
  period: "year" | "month";
  /** free trial length in days; 0 = no trial */
  trialDays: 0 | 7 | 30;
  /** up to N members (family plan) */
  members?: number;
  /** i18n key for the short description */
  descKey?: string;
  /** highlight as "most popular" */
  highlight?: boolean;
  cta: PlanCta;
};

export const CURRENCY = "€";

export const PLANS: PlanOffer[] = [
  {
    id: "yearly_individual",
    titleKey: "pw.plan.individual",
    price: "110,99",
    perMonth: "9,25",
    currency: CURRENCY,
    period: "year",
    trialDays: 30,
    descKey: "pw.plan.individualDesc",
    highlight: true,
    cta: "trial",
  },
  {
    id: "family",
    titleKey: "pw.plan.family",
    price: "146,99",
    perMonth: "12,25",
    currency: CURRENCY,
    period: "year",
    trialDays: 30,
    members: 6,
    cta: "trial",
  },
  {
    id: "lite",
    titleKey: "pw.plan.lite",
    price: "32,99",
    perMonth: "2,75",
    currency: CURRENCY,
    period: "year",
    trialDays: 7,
    descKey: "pw.plan.liteDesc",
    cta: "trial",
  },
  {
    id: "monthly",
    titleKey: "pw.plan.monthly",
    price: "19,99",
    currency: CURRENCY,
    period: "month",
    trialDays: 0,
    descKey: "pw.plan.monthlyDesc",
    cta: "unlock",
  },
];

export const DEFAULT_PLAN_ID: PlanId = "yearly_individual";

/** Feature lists for the Free vs Premium comparison (i18n keys). */
export const FREE_FEATURE_KEYS = ["pw.free1", "pw.free2", "pw.free3", "pw.free4"];
export const PREMIUM_FEATURE_KEYS = [
  "pw.prem1",
  "pw.prem2",
  "pw.prem3",
  "pw.prem4",
  "pw.prem5",
  "pw.prem6",
];
