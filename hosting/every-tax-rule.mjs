// An esbuild plugin for the module 'every-tax-rule', which imports each place's tax rules from src/tax/ so they register.
import { readdirSync } from 'node:fs';
import { resolve } from 'node:path';

export const everyTaxRule = {
  name: 'every-tax-rule',
  setup(build) {
    build.onResolve({ filter: /^every-tax-rule$/ }, () => ({ path: 'every-tax-rule', namespace: 'every-tax-rule' }));
    build.onLoad({ filter: /.*/, namespace: 'every-tax-rule' }, () => {
      const files = readdirSync('src/tax').filter(file => file.endsWith('.ts') && !['tax-rules.ts', 'calculation.ts'].includes(file)).sort();
      return { contents: files.map(file => `import ${JSON.stringify(resolve('src/tax', file))};`).join('\n'), loader: 'js', resolveDir: resolve('src/tax') };
    });
  },
};
