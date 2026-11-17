import { registerStandardTax } from './calculation.ts';

// Law and published rates checked November 2026.
registerStandardTax(
  "ET", "ETB",
  "The federal rate on share gains is 15%. For shares held at least one year the law increases acquisition cost by 30% before calculating the gain. That adjustment is negligible under this model’s mature-portfolio assumption that the withdrawal is all gain.",
  ["tax-et-amendment","tax-et-inflation"],
  ({ withdrawalLocal }) => withdrawalLocal * 0.15,
);
