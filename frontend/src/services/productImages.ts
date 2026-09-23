/**
 * Strict product-to-image registry for offline and fallback modes.
 * Maps canonical product_id to its verified authentic image CDN URL or clean SVG placeholder.
 * NEVER reuses images across unrelated products or uses generic category arrays.
 *
 * Synced from backend/app/services/catalog_fallback.py — the canonical source of truth.
 */

export const PRODUCT_IMAGE_REGISTRY: Record<string, string> = {
  "4c3049ae-10f3-5c63-b08a-8416a56c1b5a": "https://m.media-amazon.com/images/I/61X7ynACnQL._SX679_.jpg",
  "0f852853-07c2-4370-b88d-e770f1d34b18": "https://m.media-amazon.com/images/I/51dVrlj0hTL._SX679_.jpg",
  "012cf2e7-a35e-53ef-8711-5aad00c29489": "https://m.media-amazon.com/images/I/61y5-UNWNLL._SX679_.jpg",
  "7957ff81-e400-5cb4-a0e6-9135797e7c85": "https://m.media-amazon.com/images/I/71pSZbUZMxL._SX522_.jpg",
  "d65a75f8-b4bb-56ae-be17-f94de8b641c4": "https://m.media-amazon.com/images/I/61HRRrSTEQL._SX522_.jpg",
  "a7c5b7be-de3f-46df-af0c-28c6f010ffc0": "https://m.media-amazon.com/images/I/617y12kla3L.jpg",
  "236fbe49-6434-46f6-a857-4483549f0072": "https://m.media-amazon.com/images/I/61ZFj+wanLL.jpg",
  "90b32685-1c65-4691-acba-15c54c927ba8": "https://mm.digikey.com/Volume0/opasdata/d220001/derivates/3/002/622/019/C%20Series%200603%281608%20Metric%29%209.jpg",
  "311d4fff-66d6-4fb5-8f56-df2472bdeb11": "https://m.media-amazon.com/images/I/61u9f2GfHPL._SL1100_.jpg",
  "c1000000-0000-0000-0000-000000000001": "data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'500\' height=\'500\' viewBox=\'0 0 500 500\'><rect width=\'500\' height=\'500\' fill=\'%23f8fafc\'/><rect x=\'40\' y=\'40\' width=\'420\' height=\'420\' rx=\'16\' fill=\'%23f1f5f9\' stroke=\'%23cbd5e1\' stroke-width=\'2\'/><circle cx=\'250\' cy=\'200\' r=\'45\' fill=\'%23e2e8f0\'/><path d=\'M225 200 L275 200 M250 175 L250 225\' stroke=\'%2394a3b8\' stroke-width=\'3\' stroke-linecap=\'round\'/><text x=\'250\' y=\'290\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'16\' font-weight=\'600\' fill=\'%23334155\'>Image unavailable</text><text x=\'250\' y=\'325\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'13\' font-style=\'italic\' fill=\'%2394a3b8\'>Verified link not found</text></svg>",
  "c1000000-0000-0000-0000-000000000002": "https://m.media-amazon.com/images/I/618d5bS2lUL._SL1500_.jpg",
  "c1000000-0000-0000-0000-000000000003": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/m/7/y/-original-imagypv6datec8tp.jpeg?q=90",
  "c1000000-0000-0000-0000-000000000004": "https://m.media-amazon.com/images/I/710TJuHTMhL._SL1500_.jpg",
  "c1000000-0000-0000-0000-000000000005": "data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'500\' height=\'500\' viewBox=\'0 0 500 500\'><rect width=\'500\' height=\'500\' fill=\'%23f8fafc\'/><rect x=\'40\' y=\'40\' width=\'420\' height=\'420\' rx=\'16\' fill=\'%23f1f5f9\' stroke=\'%23cbd5e1\' stroke-width=\'2\'/><circle cx=\'250\' cy=\'200\' r=\'45\' fill=\'%23e2e8f0\'/><path d=\'M225 200 L275 200 M250 175 L250 225\' stroke=\'%2394a3b8\' stroke-width=\'3\' stroke-linecap=\'round\'/><text x=\'250\' y=\'290\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'16\' font-weight=\'600\' fill=\'%23334155\'>Image unavailable</text><text x=\'250\' y=\'325\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'13\' font-style=\'italic\' fill=\'%2394a3b8\'>Verified link not found</text></svg>",
  "c1000000-0000-0000-0000-000000000006": "data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'500\' height=\'500\' viewBox=\'0 0 500 500\'><rect width=\'500\' height=\'500\' fill=\'%23f8fafc\'/><rect x=\'40\' y=\'40\' width=\'420\' height=\'420\' rx=\'16\' fill=\'%23f1f5f9\' stroke=\'%23cbd5e1\' stroke-width=\'2\'/><circle cx=\'250\' cy=\'200\' r=\'45\' fill=\'%23e2e8f0\'/><path d=\'M225 200 L275 200 M250 175 L250 225\' stroke=\'%2394a3b8\' stroke-width=\'3\' stroke-linecap=\'round\'/><text x=\'250\' y=\'290\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'16\' font-weight=\'600\' fill=\'%23334155\'>Image unavailable</text><text x=\'250\' y=\'325\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'13\' font-style=\'italic\' fill=\'%2394a3b8\'>Verified link not found</text></svg>",
  "c1000000-0000-0000-0000-000000000007": "data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'500\' height=\'500\' viewBox=\'0 0 500 500\'><rect width=\'500\' height=\'500\' fill=\'%23f8fafc\'/><rect x=\'40\' y=\'40\' width=\'420\' height=\'420\' rx=\'16\' fill=\'%23f1f5f9\' stroke=\'%23cbd5e1\' stroke-width=\'2\'/><circle cx=\'250\' cy=\'200\' r=\'45\' fill=\'%23e2e8f0\'/><path d=\'M225 200 L275 200 M250 175 L250 225\' stroke=\'%2394a3b8\' stroke-width=\'3\' stroke-linecap=\'round\'/><text x=\'250\' y=\'290\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'16\' font-weight=\'600\' fill=\'%23334155\'>Image unavailable</text><text x=\'250\' y=\'325\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'13\' font-style=\'italic\' fill=\'%2394a3b8\'>Verified link not found</text></svg>",
  "c1000000-0000-0000-0000-000000000008": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/1/z/w/-enriched-transparent-original-imahg5fx53zsqcs4.png?q=90",
  "c1000000-0000-0000-0000-000000000009": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/a/z/m/g614jv-n3474ws-gaming-laptop-asus-original-imah2fk856vncuqu.jpeg?q=90",
  "c1000000-0000-0000-0000-000000000010": "data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'500\' height=\'500\' viewBox=\'0 0 500 500\'><rect width=\'500\' height=\'500\' fill=\'%23f8fafc\'/><rect x=\'40\' y=\'40\' width=\'420\' height=\'420\' rx=\'16\' fill=\'%23f1f5f9\' stroke=\'%23cbd5e1\' stroke-width=\'2\'/><circle cx=\'250\' cy=\'200\' r=\'45\' fill=\'%23e2e8f0\'/><path d=\'M225 200 L275 200 M250 175 L250 225\' stroke=\'%2394a3b8\' stroke-width=\'3\' stroke-linecap=\'round\'/><text x=\'250\' y=\'290\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'16\' font-weight=\'600\' fill=\'%23334155\'>Image unavailable</text><text x=\'250\' y=\'325\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'13\' font-style=\'italic\' fill=\'%2394a3b8\'>Verified link not found</text></svg>",
  "c1000000-0000-0000-0000-000000000011": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/h/w/b/-original-imagtzvhxxuhzr4g.jpeg?q=90",
  "c1000000-0000-0000-0000-000000000012": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/z/o/8/-original-imahg4pa9rdaem5n.jpeg?q=90",
  "c1000000-0000-0000-0000-000000000013": "https://m.media-amazon.com/images/I/71jG+e7roXL._SL1500_.jpg",
  "c1000000-0000-0000-0000-000000000014": "data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'500\' height=\'500\' viewBox=\'0 0 500 500\'><rect width=\'500\' height=\'500\' fill=\'%23f8fafc\'/><rect x=\'40\' y=\'40\' width=\'420\' height=\'420\' rx=\'16\' fill=\'%23f1f5f9\' stroke=\'%23cbd5e1\' stroke-width=\'2\'/><circle cx=\'250\' cy=\'200\' r=\'45\' fill=\'%23e2e8f0\'/><path d=\'M225 200 L275 200 M250 175 L250 225\' stroke=\'%2394a3b8\' stroke-width=\'3\' stroke-linecap=\'round\'/><text x=\'250\' y=\'290\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'16\' font-weight=\'600\' fill=\'%23334155\'>Image unavailable</text><text x=\'250\' y=\'325\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'13\' font-style=\'italic\' fill=\'%2394a3b8\'>Verified link not found</text></svg>",
  "c1000000-0000-0000-0000-000000000015": "data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'500\' height=\'500\' viewBox=\'0 0 500 500\'><rect width=\'500\' height=\'500\' fill=\'%23f8fafc\'/><rect x=\'40\' y=\'40\' width=\'420\' height=\'420\' rx=\'16\' fill=\'%23f1f5f9\' stroke=\'%23cbd5e1\' stroke-width=\'2\'/><circle cx=\'250\' cy=\'200\' r=\'45\' fill=\'%23e2e8f0\'/><path d=\'M225 200 L275 200 M250 175 L250 225\' stroke=\'%2394a3b8\' stroke-width=\'3\' stroke-linecap=\'round\'/><text x=\'250\' y=\'290\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'16\' font-weight=\'600\' fill=\'%23334155\'>Image unavailable</text><text x=\'250\' y=\'325\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'13\' font-style=\'italic\' fill=\'%2394a3b8\'>Verified link not found</text></svg>",
  "c1000000-0000-0000-0000-000000000016": "data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'500\' height=\'500\' viewBox=\'0 0 500 500\'><rect width=\'500\' height=\'500\' fill=\'%23f8fafc\'/><rect x=\'40\' y=\'40\' width=\'420\' height=\'420\' rx=\'16\' fill=\'%23f1f5f9\' stroke=\'%23cbd5e1\' stroke-width=\'2\'/><circle cx=\'250\' cy=\'200\' r=\'45\' fill=\'%23e2e8f0\'/><path d=\'M225 200 L275 200 M250 175 L250 225\' stroke=\'%2394a3b8\' stroke-width=\'3\' stroke-linecap=\'round\'/><text x=\'250\' y=\'290\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'16\' font-weight=\'600\' fill=\'%23334155\'>Image unavailable</text><text x=\'250\' y=\'325\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'13\' font-style=\'italic\' fill=\'%2394a3b8\'>Verified link not found</text></svg>",
  "c1000000-0000-0000-0000-000000000017": "data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'500\' height=\'500\' viewBox=\'0 0 500 500\'><rect width=\'500\' height=\'500\' fill=\'%23f8fafc\'/><rect x=\'40\' y=\'40\' width=\'420\' height=\'420\' rx=\'16\' fill=\'%23f1f5f9\' stroke=\'%23cbd5e1\' stroke-width=\'2\'/><circle cx=\'250\' cy=\'200\' r=\'45\' fill=\'%23e2e8f0\'/><path d=\'M225 200 L275 200 M250 175 L250 225\' stroke=\'%2394a3b8\' stroke-width=\'3\' stroke-linecap=\'round\'/><text x=\'250\' y=\'290\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'16\' font-weight=\'600\' fill=\'%23334155\'>Image unavailable</text><text x=\'250\' y=\'325\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'13\' font-style=\'italic\' fill=\'%2394a3b8\'>Verified link not found</text></svg>",
  "c1000000-0000-0000-0000-000000000018": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/t/y/4/-enriched-transparent-original-imahg5fxfzumjkgw.png?q=90",
  "c1000000-0000-0000-0000-000000000019": "data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'500\' height=\'500\' viewBox=\'0 0 500 500\'><rect width=\'500\' height=\'500\' fill=\'%23f8fafc\'/><rect x=\'40\' y=\'40\' width=\'420\' height=\'420\' rx=\'16\' fill=\'%23f1f5f9\' stroke=\'%23cbd5e1\' stroke-width=\'2\'/><circle cx=\'250\' cy=\'200\' r=\'45\' fill=\'%23e2e8f0\'/><path d=\'M225 200 L275 200 M250 175 L250 225\' stroke=\'%2394a3b8\' stroke-width=\'3\' stroke-linecap=\'round\'/><text x=\'250\' y=\'290\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'16\' font-weight=\'600\' fill=\'%23334155\'>Image unavailable</text><text x=\'250\' y=\'325\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'13\' font-style=\'italic\' fill=\'%2394a3b8\'>Verified link not found</text></svg>",
  "c1000000-0000-0000-0000-000000000020": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/c/i/q/-enriched-transparent-original-imahg5fxrxmyynwg.png?q=90",
  "c1000000-0000-0000-0000-000000000021": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/i/t/w/-original-imah3cxkepkwh9f4.jpeg?q=90",
  "c1000000-0000-0000-0000-000000000022": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/d/f/t/-original-imahg5fx8fw9svze.jpeg?q=90",
  "c1000000-0000-0000-0000-000000000023": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/computer/v/b/p/-original-imahg5fxtdu3hsuc.jpeg?q=90",
  "c1000000-0000-0000-0000-000000000024": "https://m.media-amazon.com/images/I/71XZ6r9igGL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000025": "https://m.media-amazon.com/images/I/71nmVtNbN4L._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000026": "data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'500\' height=\'500\' viewBox=\'0 0 500 500\'><rect width=\'500\' height=\'500\' fill=\'%23f8fafc\'/><rect x=\'40\' y=\'40\' width=\'420\' height=\'420\' rx=\'16\' fill=\'%23f1f5f9\' stroke=\'%23cbd5e1\' stroke-width=\'2\'/><circle cx=\'250\' cy=\'200\' r=\'45\' fill=\'%23e2e8f0\'/><path d=\'M225 200 L275 200 M250 175 L250 225\' stroke=\'%2394a3b8\' stroke-width=\'3\' stroke-linecap=\'round\'/><text x=\'250\' y=\'290\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'16\' font-weight=\'600\' fill=\'%23334155\'>Image unavailable</text><text x=\'250\' y=\'325\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'13\' font-style=\'italic\' fill=\'%2394a3b8\'>Verified link not found</text></svg>",
  "c1000000-0000-0000-0000-000000000027": "https://m.media-amazon.com/images/I/51z9ezfuiBL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000028": "https://m.media-amazon.com/images/I/71bRz-UEILL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000029": "https://m.media-amazon.com/images/I/71MFoXmeDtL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000030": "https://m.media-amazon.com/images/I/612QNnTYz0L._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000031": "https://m.media-amazon.com/images/I/81x+1vl1kCL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000032": "https://m.media-amazon.com/images/I/61I4-3x8rtL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000101": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/mobile/p/b/q/-original-imahggex2ye98xfn.jpeg?q=90",
  "c1000000-0000-0000-0000-000000000102": "https://m.media-amazon.com/images/I/71d7rfSl0wL._SL1500_.jpg",
  "c1000000-0000-0000-0000-000000000103": "https://m.media-amazon.com/images/I/71vdTR50hFL._SL1500_.jpg",
  "c1000000-0000-0000-0000-000000000104": "https://m.media-amazon.com/images/I/71GLMJ7TQiL._SL1500_.jpg",
  "c1000000-0000-0000-0000-000000000105": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/mobile/y/s/g/-original-imahgfmy2zgqvjmy.jpeg?q=90",
  "c1000000-0000-0000-0000-000000000106": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/w/z/n/-original-imah5ywfurj7gtqn.jpeg",
  "c1000000-0000-0000-0000-000000000107": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/t/g/r/-original-imahbhwhttnggfmc.jpeg",
  "c1000000-0000-0000-0000-000000000108": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/mobile/p/i/g/galaxy-m34-5g-without-charger-sm-m346b-samsung-original-imagrhrhbuja8grh.jpeg?q=90",
  "c1000000-0000-0000-0000-000000000109": "https://m.media-amazon.com/images/I/717Qo4MH97L._SL1500_.jpg",
  "c1000000-0000-0000-0000-000000000110": "https://rukminim2.flixcart.com/image/312/312/xif0q/mobile/m/i/u/12r-cph2585-oneplus-original-imah9zk5nnfqyurm.jpeg?q=70",
  "c1000000-0000-0000-0000-000000000111": "https://m.media-amazon.com/images/I/6175SlKKECL._SL1500_.jpg",
  "c1000000-0000-0000-0000-000000000112": "https://m.media-amazon.com/images/I/71r69Y7BSeL._SL1500_.jpg",
  "c1000000-0000-0000-0000-000000000113": "https://m.media-amazon.com/images/I/61iLQG-KbLL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000114": "https://m.media-amazon.com/images/I/61pTBxDPd-L._SY879_.jpg",
  "c1000000-0000-0000-0000-000000000115": "https://m.media-amazon.com/images/I/71d1ytcCntL._SL1500_.jpg",
  "c1000000-0000-0000-0000-000000000116": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/mobile/x/j/m/-original-imagwubk2ky9v2gz.jpeg?q=90",
  "c1000000-0000-0000-0000-000000000117": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/9/f/c/-original-imahfk4xxgusghq8.jpeg",
  "c1000000-0000-0000-0000-000000000118": "https://m.media-amazon.com/images/I/71JxLJvl5dL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000119": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/q/r/y/12-5g-iqoo-12-5g-iqoo-original-imagwhuqe6gwht6c.jpeg",
  "c1000000-0000-0000-0000-000000000120": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/c/g/a/-original-imahfptqg23vghss.jpeg",
  "c1000000-0000-0000-0000-000000000121": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/5/t/j/edge-50-fusion-pb300002in-motorola-original-imahywzrfagkuyxx.jpeg",
  "c1000000-0000-0000-0000-000000000122": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/k/w/a/-original-imagt5ugmkks2ep7.jpeg",
  "c1000000-0000-0000-0000-000000000123": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/d/q/y/gt-6t-5g-rmx3853-realme-original-imahfddqupz7zzmh.jpeg",
  "c1000000-0000-0000-0000-000000000124": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/0/i/o/neo9-pro-i2304-iqoo-original-imagyg968j7pafeg.jpeg",
  "c1000000-0000-0000-0000-000000000125": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/o/k/x/z9s-pro-5g-z9s-pro-5g-iqoo-original-imah46j7jzhchck7.jpeg",
  "c1000000-0000-0000-0000-000000000126": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/s/l/6/narzo-70-pro-5g-narzo-70-pro-5g-realme-original-imahf4hhqzfnjmkd.jpeg",
  "c1000000-0000-0000-0000-000000000127": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/x/0/r/m6-pro-5g-mzb0eqjin-poco-original-imags3e7beqmyfje.jpeg",
  "c1000000-0000-0000-0000-000000000128": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/c/w/b/m15-sm-m156b-samsung-original-imahedag4bsyqjsz.jpeg",
  "c1000000-0000-0000-0000-000000000129": "data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'500\' height=\'500\' viewBox=\'0 0 500 500\'><rect width=\'500\' height=\'500\' fill=\'%23f8fafc\'/><rect x=\'40\' y=\'40\' width=\'420\' height=\'420\' rx=\'16\' fill=\'%23f1f5f9\' stroke=\'%23cbd5e1\' stroke-width=\'2\'/><circle cx=\'250\' cy=\'200\' r=\'45\' fill=\'%23e2e8f0\'/><path d=\'M225 200 L275 200 M250 175 L250 225\' stroke=\'%2394a3b8\' stroke-width=\'3\' stroke-linecap=\'round\'/><text x=\'250\' y=\'290\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'16\' font-weight=\'600\' fill=\'%23334155\'>OnePlus%20Nord%204%205G%20%28Mercurial%20Silver</text><text x=\'250\' y=\'325\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'14\' font-weight=\'500\' fill=\'%2364748b\'>[Front View]</text><text x=\'250\' y=\'365\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'13\' font-style=\'italic\' fill=\'%2394a3b8\'>Image unavailable</text></svg>",
  "c1000000-0000-0000-0000-000000000130": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/g/a/e/open-cph2551-oneplus-original-imagv2r4xvkjqcrj.jpeg",
  "c1000000-0000-0000-0000-000000000131": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/p/b/7/-original-imahggetywqjzwg6.jpeg",
  "c1000000-0000-0000-0000-000000000132": "https://rukminim2.flixcart.com/image/480/640/xif0q/mobile/t/f/q/-original-imahfvuahbmttxgu.jpeg",
  "c1000000-0000-0000-0000-000000000201": "https://m.media-amazon.com/images/I/61+btxzpfDL._SL1500_.jpg",
  "c1000000-0000-0000-0000-000000000202": "https://m.media-amazon.com/images/I/61wAWttbWrL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000203": "https://m.media-amazon.com/images/I/51--iaLfgWL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000204": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/headphone/p/2/v/wf-1000xm5-sony-enriched-transparent-original-imagtak4zdhzhffc.png?q=90",
  "c1000000-0000-0000-0000-000000000205": "https://m.media-amazon.com/images/I/51ZR4lyxBHL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000206": "https://m.media-amazon.com/images/I/51JbsHSktkL._SL1500_.jpg",
  "c1000000-0000-0000-0000-000000000207": "https://m.media-amazon.com/images/I/61SUj2aKoEL._SL1500_.jpg",
  "c1000000-0000-0000-0000-000000000208": "https://m.media-amazon.com/images/I/81U3QW4lCcL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000209": "https://m.media-amazon.com/images/I/716++4xC2wL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000210": "https://m.media-amazon.com/images/I/71z2y-w+hmL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000211": "https://m.media-amazon.com/images/I/71G5OkSr2zL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000212": "https://m.media-amazon.com/images/I/511M6l6E5bL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000213": "https://m.media-amazon.com/images/I/61u1VALn6JL._SL1500_.jpg",
  "c1000000-0000-0000-0000-000000000214": "https://m.media-amazon.com/images/I/61leGjTDm0L._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000215": "https://m.media-amazon.com/images/I/41ELxYw4xAL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000216": "https://m.media-amazon.com/images/I/61e0+8QzVBL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000217": "https://m.media-amazon.com/images/I/51ni1o+keWL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000218": "https://m.media-amazon.com/images/I/51F-Ok9xuzL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000219": "https://m.media-amazon.com/images/I/71St1R5DFGL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000220": "https://m.media-amazon.com/images/I/617BfhOXfpL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000221": "data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'500\' height=\'500\' viewBox=\'0 0 500 500\'><rect width=\'500\' height=\'500\' fill=\'%23f8fafc\'/><rect x=\'40\' y=\'40\' width=\'420\' height=\'420\' rx=\'16\' fill=\'%23f1f5f9\' stroke=\'%23cbd5e1\' stroke-width=\'2\'/><circle cx=\'250\' cy=\'200\' r=\'45\' fill=\'%23e2e8f0\'/><path d=\'M225 200 L275 200 M250 175 L250 225\' stroke=\'%2394a3b8\' stroke-width=\'3\' stroke-linecap=\'round\'/><text x=\'250\' y=\'290\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'16\' font-weight=\'600\' fill=\'%23334155\'>Audio-Technica%20ATH-M50xBT2%20Wireless</text><text x=\'250\' y=\'325\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'14\' font-weight=\'500\' fill=\'%2364748b\'>[Front View]</text><text x=\'250\' y=\'365\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'13\' font-style=\'italic\' fill=\'%2394a3b8\'>Image unavailable</text></svg>",
  "c1000000-0000-0000-0000-000000000222": "https://m.media-amazon.com/images/I/81zcnWFPwVS._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000223": "https://m.media-amazon.com/images/I/51fqxfdHIcL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000224": "https://m.media-amazon.com/images/I/516jDyX+YrL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000225": "data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'500\' height=\'500\' viewBox=\'0 0 500 500\'><rect width=\'500\' height=\'500\' fill=\'%23f8fafc\'/><rect x=\'40\' y=\'40\' width=\'420\' height=\'420\' rx=\'16\' fill=\'%23f1f5f9\' stroke=\'%23cbd5e1\' stroke-width=\'2\'/><circle cx=\'250\' cy=\'200\' r=\'45\' fill=\'%23e2e8f0\'/><path d=\'M225 200 L275 200 M250 175 L250 225\' stroke=\'%2394a3b8\' stroke-width=\'3\' stroke-linecap=\'round\'/><text x=\'250\' y=\'290\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'16\' font-weight=\'600\' fill=\'%23334155\'>boAt%20Nirvana%20Ion%20TWS%20Earbuds%20-%20Char</text><text x=\'250\' y=\'325\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'14\' font-weight=\'500\' fill=\'%2364748b\'>[Front View]</text><text x=\'250\' y=\'365\' text-anchor=\'middle\' font-family=\'-apple-system, BlinkMacSystemFont, sans-serif\' font-size=\'13\' font-style=\'italic\' fill=\'%2394a3b8\'>Image unavailable</text></svg>",
  "c1000000-0000-0000-0000-000000000226": "https://m.media-amazon.com/images/I/61APOA2BNFL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000227": "https://m.media-amazon.com/images/I/71Z9KK9-zvL._SX679_.jpg",
  "c1000000-0000-0000-0000-000000000228": "https://m.media-amazon.com/images/I/51qMK4q-NVL._SX679_.jpg",
  "c2000000-0000-0000-0000-000000000001": "https://m.media-amazon.com/images/I/61qtydPJLBL._SX679_.jpg",
  "c2000000-0000-0000-0000-000000000002": "https://rukminim2.flixcart.com/image/1000/1000/kerfl3k0/electronic-hobby-kit/x/s/z/wireless-module-ch340-nodemcu-v3-lua-wifi-internet-of-things-original-imafvdhadmhxzfz5.jpeg?q=90",
  "c2000000-0000-0000-0000-000000000003": "https://rukminim2.flixcart.com/image/1000/1000/kfeamq80/learning-toy/q/r/7/uno-r3-board-atmega328p-arduino-original-imafvuwgc236fhzx.jpeg?q=90",
  "c2000000-0000-0000-0000-000000000004": "https://rukminim2.flixcart.com/image/480/480/kf4ajrk0/electronic-hobby-kit/c/z/c/arduino-mega-2560-r3-compatible-board-with-atmega2560-ch340-with-original-imafvnfb6zr3v7a6.jpeg?q=80",
  "c2000000-0000-0000-0000-000000000005": "https://m.media-amazon.com/images/I/61mpMH5TzkL._SL1500_.jpg",
  "c2000000-0000-0000-0000-000000000006": "https://rukminim2.flixcart.com/image/480/480/xif0q/motherboard/l/p/p/raspberry-pi-5-8gb-5-8gb-ram-64-bit-quad-core-arm-cortex-a76-original-imagudmuhqcjvtgd.jpeg?q=80",
  "c2000000-0000-0000-0000-000000000007": "https://rukminim2.flixcart.com/image/1000/1330/l51d30w0/motherboard/s/c/n/pico-w-pico-w-wireless-raspberry-pi-original-imagfshhgdxpga6t.jpeg?q=90",
  "c2000000-0000-0000-0000-000000000008": "https://rukminim2.flixcart.com/image/480/480/jm81zm80/electronic-hobby-kit/p/4/r/dht11-digital-temperature-and-humidity-temperature-dht-11-sensor-original-imaf95njtbvbzmfe.jpeg?q=80",
  "c2000000-0000-0000-0000-000000000009": "https://rukminim2.flixcart.com/image/1000/1330/l3os4280/electronic-hobby-kit/n/d/y/dht22-am2302-digital-temperature-and-humidity-sensor-iduino-original-imagerh2pfshgamf.jpeg?q=90",
  "c2000000-0000-0000-0000-000000000010": "https://rukminim2.flixcart.com/image/1000/1000/jkzrc7k0/electronic-hobby-kit/g/p/n/breakout-temperature-humidity-barometric-pressure-bme280-digital-original-imaf87xw88vx2ng9.jpeg?q=90",
  "c2000000-0000-0000-0000-000000000011": "https://rukminim2.flixcart.com/image/480/480/xif0q/sensor/l/u/e/pir-motion-sensor-detector-module-hc-sr501-circuitcomponents-resized-original-imag9hcfy9j2qmyj.jpeg",
  "c2000000-0000-0000-0000-000000000012": "https://rukminim2.flixcart.com/image/1000/1330/xif0q/electronic-hobby-kit/b/k/c/hc-sr04-ultrasonic-distance-measurement-transducer-module-sensor-resized-original-imag3wfwzpsxffv7.jpeg?q=90",
  "c2000000-0000-0000-0000-000000000013": "https://rukminim2.flixcart.com/image/480/480/kws5hu80/sensor/c/3/m/mq2-mq-2-gas-sensor-module-smoke-methane-butane-detection-original-imag9dntwqwpjwvf.jpeg?q=80",
  "c2000000-0000-0000-0000-000000000014": "https://rukminim2.flixcart.com/image/480/480/electronic-hobby-kit/z/x/z/bh1750-digital-light-sensor-module-sunrobotics-original-imaekybddhfs8ruy.jpeg?q=80",
  "c2000000-0000-0000-0000-000000000015": "https://rukminim2.flixcart.com/image/1000/1330/kgzg8sw0/electronic-hobby-kit/4/w/c/1-channel-5v-10a-relay-module-with-optocoupler-ac-and-dc-original-imafx3m9zfmzwf7k.jpeg?q=90",
  "c2000000-0000-0000-0000-000000000016": "https://rukminim2.flixcart.com/image/1000/1330/j9a8fww0/learning-toy/g/3/d/optocoupler-4-channel-5v-relay-module-relay-control-for-arduino-original-imaez2fdw7wky2uz.jpeg?q=90",
  "c2000000-0000-0000-0000-000000000017": "https://rukminim2.flixcart.com/image/480/480/kq9ta4w0/learning-toy/e/g/r/8-channel-5v-relay-board-module-sunrobotics-original-imag4bbgwgfzjuse.jpeg?q=80",
  "c2000000-0000-0000-0000-000000000018": "https://rukminim2.flixcart.com/image/480/640/xif0q/electronic-hobby-kit/c/d/e/l298n-motor-driver-module-dual-h-bridge-dc-stepper-for-arduino-original-imaghzsnvz5zqmse.jpeg?q=80",
  "c2000000-0000-0000-0000-000000000019": "https://rukminim2.flixcart.com/image/480/640/xif0q/electronic-hobby-kit/e/i/6/servo-motor-sg90-tower-pro-sg90-servo-motor-9-gms-mini-micro-original-imah79xdpfwyetzk.jpeg?q=80",
  "c2000000-0000-0000-0000-000000000020": "https://rukminim2.flixcart.com/image/480/480/kngd0nk0/learning-toy/v/e/x/lora-module-sx1278-433m-10km-ra-02-ai-thinker-wireless-spread-original-imag24pr2qqmncgp.jpeg?q=80",
  "c2000000-0000-0000-0000-000000000021": "https://rukminim2.flixcart.com/image/480/480/j1xvzbk0/learning-toy/j/s/f/ublox-neo-6m-gps-module-with-ceramic-antenna-logicinside-original-imaetdhpaukyhw94.jpeg?q=80",
  "c2000000-0000-0000-0000-000000000022": "https://rukminim2.flixcart.com/image/480/480/xif0q/electronic-hobby-kit/j/r/p/0-96-inch-128x64-iic-i2c-oled-display-module-blue-ssd1306-driver-original-imagsz9n9hme2h55.jpeg?q=80",
  "c2000000-0000-0000-0000-000000000023": "https://rukminim2.flixcart.com/image/480/640/krntoy80/electronic-hobby-kit/k/h/f/16x2-lcd-blue-with-i2c-module-for-ar-duino-trustech-original-imag5et9sbd8vdye.jpeg?q=80",
  "c2000000-0000-0000-0000-000000000024": "https://rukminim2.flixcart.com/image/480/480/xif0q/electronic-hobby-kit/4/b/o/lm2596-dc-dc-buck-converter-4-5-40v-3a-step-down-voltage-original-imagsrfhxkjkbz4h.jpeg?q=80",
  "c2000000-0000-0000-0000-000000000025": "https://rukminim2.flixcart.com/image/1000/1000/kwb07m80/electronic-hobby-kit/l/7/f/i2c-bi-directional-logic-level-converter-4-channel-pack-of-2-original-imaekz3yamqrpkeq.jpeg?q=90",
  "c2000000-0000-0000-0000-000000000026": "https://rukminim2.flixcart.com/image/480/480/koynr0w0/electronic-hobby-kit/5/y/b/gy-521-mpu-6050-mpu6050-3-axis-accelerometer-gyroscope-module-6-original-imag3anysnzb9m5z.jpeg?q=80",
  "c2000000-0000-0000-0000-000000000027": "https://rukminim2.flixcart.com/image/480/480/xif0q/electronic-hobby-kit/f/v/r/tcrt-5000-infrared-ir-dual-channel-line-tracking-sensor-harical-original-imagrtdhyhc4bmmg.jpeg?q=80",
  "c2000000-0000-0000-0000-000000000028": "https://rukminim2.flixcart.com/image/480/480/jk5r3bk0/electronic-hobby-kit/x/5/t/mq135-mq-135-air-quality-sensor-hazardous-gas-detection-module-original-imaf7kska9yekszk.jpeg?q=80",
};

export const IMAGE_UNAVAILABLE_PLACEHOLDER =
  "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='400' viewBox='0 0 400 400'><rect width='400' height='400' fill='%23f1f5f9'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='16' fill='%2364748b'>Image unavailable</text></svg>";

/**
 * Resolves verified product image strictly by product identity.
 * Validates that image belongs to product.id / product.product_id.
 * If external_product_id is provided, verifies that as well.
 * If unverified, cleanly returns 'Image unavailable' placeholder.
 * NEVER substitutes an image from another product.
 */
export function resolveProductImage(item?: {
  id?: string;
  product_id?: string;
  external_product_id?: string | null;
  asin?: string | null;
  product_name?: string;
  product_image?: string;
  image_url?: string;
  images?: Array<{
    image_id?: string;
    product_id?: string;
    external_product_id?: string | null;
    image_url?: string;
    image_type?: string;
    source?: string;
    verified?: boolean;
  }>;
}): string {
  if (!item) return IMAGE_UNAVAILABLE_PLACEHOLDER;

  const targetId = item.product_id || item.id;
  const targetExtId = item.external_product_id || item.asin;

  // 1. Check verified images list on the product object
  if (item.images && Array.isArray(item.images) && item.images.length > 0 && targetId) {
    const candidate = item.images.find((img) => {
      if (!img || !img.image_url) return false;
      if (img.product_id && img.product_id !== targetId) return false;
      if (targetExtId && img.external_product_id && img.external_product_id !== targetExtId) return false;
      return img.verified === true;
    });
    if (candidate && candidate.image_url) {
      return candidate.image_url;
    }
  }

  // 2. Strict lookup in canonical PRODUCT_IMAGE_REGISTRY by targetId
  if (targetId && PRODUCT_IMAGE_REGISTRY[targetId]) {
    const regUrl = PRODUCT_IMAGE_REGISTRY[targetId];
    if (regUrl && !regUrl.includes("example.com")) {
      return regUrl;
    }
  }

  // 3. Direct candidate image if present and strictly valid
  const direct = item.product_image || item.image_url;
  if (direct && direct.trim().length > 0 && !direct.includes("example.com")) {
    if (direct.startsWith("data:image/svg") || direct.includes("m.media-amazon.com") || direct.includes("flipkart.com") || direct.includes("rukminim")) {
      return direct;
    }
  }

  // 4. Fallback rule: Clean placeholder stating 'Image unavailable'
  // NEVER substitute an image from another product.
  return IMAGE_UNAVAILABLE_PLACEHOLDER;
}
