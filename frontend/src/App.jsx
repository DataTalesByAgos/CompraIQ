import React, { useState, useMemo, useRef, useEffect } from 'react';
import {
  CreditCard,
  Building2,
  Wallet,
  ShoppingBag,
  Sparkles,
  Check,
  ChevronRight,
  Trash2,
  Plus,
  TrendingDown,
  DollarSign,
  Maximize2,
  Info
} from 'lucide-react';

// Animated number counter component
function AnimatedTotal({ value }) {
  const [displayed, setDisplayed] = useState(value);
  const prevRef = useRef(value);
  const rafRef = useRef(null);

  useEffect(() => {
    const start = prevRef.current;
    const end = value;
    if (start === end) return;
    const duration = 350; // ms
    const startTime = performance.now();

    const step = (now) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayed(Math.round(start + (end - start) * eased));
      if (progress < 1) {
        rafRef.current = requestAnimationFrame(step);
      } else {
        prevRef.current = end;
      }
    };
    rafRef.current = requestAnimationFrame(step);
    return () => cancelAnimationFrame(rafRef.current);
  }, [value]);

  return <span>${Math.ceil(displayed).toLocaleString('es-AR', { maximumFractionDigits: 0 })}</span>;
}
const fmt = (n) => Math.ceil(n ?? 0).toLocaleString('es-AR', { maximumFractionDigits: 0 });

// Benefit definitions (onboarding database)
const BENEFIT_CATEGORIES = [
  { id: 'bancos', name: 'Bancos', icon: Building2, desc: 'Santander, Galicia, Provincia, etc.' },
  { id: 'tarjetas', name: 'Tarjetas', icon: CreditCard, desc: 'Visa, Mastercard, Amex' },
  { id: 'billeteras', name: 'Billeteras', icon: Wallet, desc: 'Cuenta DNI, MODO, MP' },
  { id: 'clubes', name: 'Clubes', icon: ShoppingBag, desc: 'Coto Club, Comunidad Dia, Jumbo+' }
];

const SPECIFIC_BENEFITS = {
  bancos: [
    { id: 'galicia', name: 'Banco Galicia', subName: 'Mastercard/Visa Galicia', promo: '15% Viernes en Coto', value: 15, day: 'viernes', target: 'Coto', limit: 1500, category: 'almacen' },
    { id: 'provincia', name: 'Banco Provincia', subName: 'Visa Provincia', promo: '10% Miércoles en Carrefour', value: 10, day: 'miércoles', target: 'Carrefour', limit: 1000, category: 'alimentos' },
    { id: 'santander', name: 'Banco Santander', subName: 'Visa Santander', promo: '10% Miércoles en Jumbo', value: 10, day: 'miércoles', target: 'Jumbo', limit: 1200, category: 'all' }
  ],
  tarjetas: [
    { id: 'visa', name: 'Visa', subName: 'Visa General', promo: '10% Lunes en Carrefour', value: 10, day: 'lunes', target: 'Carrefour', limit: 800, category: 'all' },
    { id: 'mastercard', name: 'Mastercard', subName: 'Mastercard General', promo: '10% Jueves en Dia', value: 10, day: 'jueves', target: 'Dia', limit: 800, category: 'all' }
  ],
  billeteras: [
    { id: 'cuentadni', name: 'Cuenta DNI', subName: 'Billetera BAPRO', promo: '20% Miércoles en Dia y Carrefour', value: 20, day: 'miércoles', target: 'Dia', limit: 2000, category: 'alimentos' },
    { id: 'modo', name: 'MODO', subName: 'MODO App', promo: '15% Sábado en Jumbo y Disco', value: 15, day: 'sábado', target: 'Jumbo', limit: 1500, category: 'all' }
  ],
  clubes: [
    { id: 'cotoclub', name: 'Coto Club', subName: 'Fidelidad Coto', promo: '10% Lunes y Miércoles en Coto', value: 10, day: 'miércoles', target: 'Coto', limit: 9999, category: 'all' },
    { id: 'comunidaddia', name: 'Comunidad Dia', subName: 'Socio Dia', promo: '15% Martes en Dia', value: 15, day: 'martes', target: 'Dia', limit: 9999, category: 'limpieza' }
  ]
};

// Base products list for Quick Add with Brand/Variant options
const PRODUCT_CATALOG = [
  {
    name: 'Leche Entera',
    category: 'Lácteos',
    basePrices: { Carrefour: 1250, Dia: 1190, Coto: 1290, Jumbo: 1310, Disco: 1310, Vea: 1280 },
    variants: [
      { brand: 'La Serenísima', factor: 1.15 },
      { brand: 'Armonía', factor: 0.90 },
      { brand: 'Carrefour Classic', factor: 0.85 }
    ]
  },
  {
    name: 'Yogur de Vainilla',
    category: 'Lácteos',
    basePrices: { Carrefour: 790, Dia: 820, Coto: 850, Jumbo: 850, Disco: 850, Vea: 840 },
    variants: [
      { brand: 'Yogs', factor: 1.10 },
      { brand: 'Sancor', factor: 1.00 },
      { brand: 'Dia %', factor: 0.80 }
    ]
  },
  {
    name: 'Fideos Tallarines',
    category: 'Básicos de Almacén',
    basePrices: { Carrefour: 1450, Dia: 1390, Coto: 1490, Jumbo: 1520, Disco: 1520, Vea: 1480 },
    variants: [
      { brand: 'Matarazzo', factor: 1.20 },
      { brand: 'Lucchetti', factor: 1.00 },
      { brand: 'Favorita', factor: 0.85 }
    ]
  },
  {
    name: 'Aceite de Girasol',
    category: 'Básicos de Almacén',
    basePrices: { Carrefour: 3400, Dia: 3250, Coto: 3450, Jumbo: 3500, Disco: 3500, Vea: 3420 },
    variants: [
      { brand: 'Natura', factor: 1.25 },
      { brand: 'Cocinero', factor: 1.05 },
      { brand: 'Cañuelas', factor: 0.95 }
    ]
  },
  {
    name: 'Carne Picada Vacuna (kg)',
    category: 'Carnicería y Pescadería',
    basePrices: { Carrefour: 7800, Dia: 7500, Coto: 6900, Jumbo: 7990, Disco: 7990, Vea: 7750 },
    variants: [
      { brand: 'Novillito Premium', factor: 1.20 },
      { brand: 'Común', factor: 0.90 }
    ]
  },
  {
    name: 'Pechuga de Pollo (kg)',
    category: 'Carnicería y Pescadería',
    basePrices: { Carrefour: 5200, Dia: 4900, Coto: 4700, Jumbo: 5400, Disco: 5400, Vea: 5100 },
    variants: [
      { brand: 'Pollo de Campo', factor: 1.15 },
      { brand: 'Cresta Roja', factor: 1.00 }
    ]
  },
  {
    name: 'Detergente Lavavajillas',
    category: 'Limpieza del Hogar',
    basePrices: { Carrefour: 2390, Dia: 2450, Coto: 2500, Jumbo: 2590, Disco: 2590, Vea: 2490 },
    variants: [
      { brand: 'Magistral', factor: 1.30 },
      { brand: 'Ala', factor: 1.00 },
      { brand: 'Querubín', factor: 0.85 }
    ]
  },
  {
    name: 'Jabón Líquido Ropa',
    category: 'Limpieza del Hogar',
    basePrices: { Carrefour: 4800, Dia: 4600, Coto: 4900, Jumbo: 5100, Disco: 5100, Vea: 4950 },
    variants: [
      { brand: 'Ariel', factor: 1.35 },
      { brand: 'Skip', factor: 1.25 },
      { brand: 'Drive', factor: 0.95 }
    ]
  },
  {
    name: 'Gaseosa Cola 2.25L',
    category: 'Bebidas sin Alcohol',
    basePrices: { Carrefour: 3100, Dia: 2990, Coto: 3150, Jumbo: 3250, Disco: 3250, Vea: 3180 },
    variants: [
      { brand: 'Coca-Cola Sabor Original', factor: 1.30 },
      { brand: 'Coca-Cola Zero', factor: 1.25 },
      { brand: 'Manaos Cola', factor: 0.60 }
    ]
  }
];

export default function App() {
  const [activeTab, setActiveTab] = useState('benefits'); // 'benefits', 'calendar', 'cart'
  const [selectedCategory, setSelectedCategory] = useState(null); // Bancos, etc.

  // Real promotions state from backend
  const [dynamicPromotions, setDynamicPromotions] = useState({
    bancos: [], tarjetas: [], billeteras: [], clubes: []
  });

  const [selectedBenefits, setSelectedBenefits] = useState(() => {
    const saved = localStorage.getItem('compraiq_benefits');
    return saved ? JSON.parse(saved) : [];
  });

  const [cart, setCart] = useState([]);
  const [customItemText, setCustomItemText] = useState('');
  const [selectedDaySimulated, setSelectedDaySimulated] = useState('miércoles');
  const [activeModalItemIndex, setActiveModalItemIndex] = useState(null); // Track item variant modal state
  const [activeBenefitsDay, setActiveBenefitsDay] = useState('miércoles');
  const [carouselStartIdx, setCarouselStartIdx] = useState(0);
  const [showAllStores, setShowAllStores] = useState(false);

  const [popularProducts, setPopularProducts] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const searchDebounceRef = useRef(null);

  // Derived: the store linked to the first selected benefit
  const targetStore = (
    selectedBenefits.length > 0 &&
    selectedBenefits[0].entries &&
    selectedBenefits[0].entries[0]?.supermercado
  ) || 'Carrefour';

  // Load popular products when targetStore changes
  React.useEffect(() => {
    fetch(`http://localhost:5000/api/products/popular?store=${encodeURIComponent(targetStore)}&limit=6`)
      .then(r => r.json())
      .then(data => {
        if (Array.isArray(data)) setPopularProducts(data);
      })
      .catch(() => {});
  }, [targetStore]);

  // Load promotions from backend – grouped by benefit name
  React.useEffect(() => {
    fetch('http://localhost:5000/api/promotions')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          // We collect individual promos but group by (beneficio + tipo_beneficio)
          const catMap = { bancos: {}, tarjetas: {}, billeteras: {}, clubes: {} };

          data.forEach(promo => {
            let cat = 'bancos';
            if (promo.tipo_beneficio === 'billetera') cat = 'billeteras';
            else if (promo.tipo_beneficio === 'club') cat = 'clubes';
            else if (promo.tipo_beneficio === 'tarjeta') cat = 'tarjetas';
            else if (promo.tipo_beneficio === 'prensa') cat = 'clubes';

            const key = promo.beneficio;
            if (!catMap[cat][key]) {
              catMap[cat][key] = {
                id: key,           // unique key = benefit name
                name: promo.beneficio,
                tipo_beneficio: promo.tipo_beneficio,
                // Entries = list of { supermercado, dia_semana, valor, tope, id }
                entries: []
              };
            }
            catMap[cat][key].entries.push({
              id: promo.id,
              supermercado: promo.supermercado,
              day: promo.dia_semana,
              value: Number(promo.valor),
              limit: promo.tope_descuento_pesos ? Number(promo.tope_descuento_pesos) : 9999
            });
          });

          // Convert dicts to arrays
          const categorized = {};
          for (const cat of Object.keys(catMap)) {
            categorized[cat] = Object.values(catMap[cat]);
          }
          setDynamicPromotions(categorized);
        }
      })
      .catch(err => console.error('Error fetching promotions from backend:', err));
  }, []);

  // Persist selected benefits – benefit here is the grouped card object
  const handleToggleBenefit = (benefit) => {
    let updated;
    const isAlreadySelected = selectedBenefits.some(b => b.id === benefit.id);

    if (isAlreadySelected) {
      updated = selectedBenefits.filter(b => b.id !== benefit.id);
    } else {
      // Find what days this benefit is active for
      const activeDays = benefit.entries.map(e => e.day.toLowerCase());

      // If the benefit has entries matching the currently selected simulated day, allow selection.
      // Otherwise, switch the selectedDaySimulated to this benefit's first active day and reset other benefits
      // because we only simulate a single day's cart trip.
      const matchesCurrentDay = activeDays.includes(selectedDaySimulated.toLowerCase());

      if (matchesCurrentDay) {
        updated = [...selectedBenefits, benefit];
      } else {
        // Switch day to the first day of this benefit, clearing other non-matching benefits
        const newDay = activeDays[0];
        setSelectedDaySimulated(newDay);
        updated = [benefit];
      }
    }
    setSelectedBenefits(updated);
    localStorage.setItem('compraiq_benefits', JSON.stringify(updated));
  };

  // Image resolution helper
  const getBenefitImage = (name) => {
    const n = name.toLowerCase();
    if (n.includes('cuenta dni')) return '/visuales/billeteras_virtuales/cuenta_dni.webp';
    if (n.includes('modo')) return '/visuales/billeteras_virtuales/modo.webp';
    if (n.includes('mercado pago')) return '/visuales/billeteras_virtuales/mercado_pago.webp';
    if (n.includes('bna+')) return '/visuales/billeteras_virtuales/BNA+.webp';
    if (n.includes('personal pay')) return '/visuales/billeteras_virtuales/personal_pay.webp';
    if (n.includes('prex')) return '/visuales/billeteras_virtuales/prex.webp';
    if (n.includes('galicia')) return '/visuales/bancos/galicia.png';
    if (n.includes('provincia')) return '/visuales/bancos/provincia.png';
    if (n.includes('santander')) return '/visuales/bancos/santander.png';
    if (n.includes('macro')) return '/visuales/bancos/macro.png';
    if (n.includes('nacion') || n.includes('bna')) return '/visuales/bancos/nacion.png';
    if (n.includes('bbva')) return '/visuales/bancos/bbva.png';
    if (n.includes('patagonia')) return '/visuales/bancos/patagonia.png';
    if (n.includes('credicoop')) return '/visuales/bancos/credicoop.png';
    if (n.includes('superville') || n.includes('supervielle')) return '/visuales/bancos/superville.png';
    if (n.includes('ciudad')) return '/visuales/bancos/ciudad.png';
    if (n.includes('columbia')) return '/visuales/bancos/columbia.png';
    if (n.includes('icbc')) return '/visuales/bancos/icbc.png';
    if (n.includes('santa fe')) return '/visuales/bancos/santaFe.png';
    if (n.includes('san juan')) return '/visuales/bancos/SanJuan.png';
    if (n.includes('santa cruz')) return '/visuales/bancos/SantaCruz.png';
    if (n.includes('entre rios')) return '/visuales/bancos/NuevoBancoEntreRios.png';
    if (n.includes('365') || n.includes('clarin')) return '/visuales/clubesydescuentos/clarin-365.webp';
    if (n.includes('la nacion')) return '/visuales/clubesydescuentos/Club_La_Nacion.avif';
    if (n.includes('coto club') || n.includes('comunidad coto')) return '/visuales/clubesydescuentos/Comunidad_Coto.png';
    if (n.includes('club dia') || n.includes('comunidad dia')) return null;
    if (n.includes('visa')) return '/visuales/tarjetas_debito/tarjetas/visa.png';
    if (n.includes('mastercard')) return '/visuales/tarjetas_debito/tarjetas/mastercard.png';
    if (n.includes('american express') || n.includes('amex')) return '/visuales/tarjetas_debito/tarjetas/americanExpress.png';
    if (n.includes('naranja')) return '/visuales/tarjetas_debito/naranja.webp';
    if (n.includes('cabal')) return '/visuales/tarjetas_debito/tarjetas/Cabal.png';
    return null;
  };

  const getSupermarketImage = (store) => {
    const s = store.toLowerCase();
    if (s === 'coto') return '/visuales/spk_assets/coto.webp';
    if (s === 'carrefour') return '/visuales/spk_assets/carrefour.svg';
    if (s === 'dia') return null; // no dia.svg in folder, skip
    if (s === 'jumbo') return '/visuales/spk_assets/jumbo.svg';
    if (s === 'disco') return '/visuales/spk_assets/disco.svg';
    if (s === 'vea') return '/visuales/spk_assets/vea.webp';
    return null;
  };

  const DAY_ABBR = {
    lunes: 'Lun', martes: 'Mar', 'miércoles': 'Mié',
    jueves: 'Jue', viernes: 'Vie', sábado: 'Sáb', domingo: 'Dom'
  };

  const handleClearBenefits = () => {
    setSelectedBenefits([]);
    localStorage.removeItem('compraiq_benefits');
  };

  // Add Item to cart — supports both real DB products and legacy catalog shape
  const handleAddItem = (product) => {
    // Normalize: DB products use { nombre, prices } — legacy used { name, basePrices }
    const normalizedName = product.nombre || product.name;
    const normalizedPrices = product.prices || product.basePrices || {};

    const exists = cart.find(item => item.name === normalizedName);
    if (exists) {
      setCart(cart.map(item =>
        item.name === normalizedName ? { ...item, quantity: item.quantity + 1 } : item
      ));
    } else {
      setCart([...cart, {
        name: normalizedName,
        categoria: product.categoria || product.category || 'General',
        presentacion: product.presentacion || '',
        product_id: product.product_id || null,
        basePrices: normalizedPrices,
        quantity: 1
      }]);
    }
  };

  const handleAddCustomItem = (e) => {
    e.preventDefault();
    if (!customItemText.trim()) return;

    // If there's a search result highlighted, add first result
    if (searchResults.length > 0) {
      handleAddItem(searchResults[0]);
    } else {
      // Fallback: add as free-text item (no real price data)
      setCart([...cart, {
        name: customItemText.trim(),
        categoria: 'General',
        presentacion: '',
        product_id: null,
        basePrices: { Carrefour: 0, Dia: 0, Coto: 0, Jumbo: 0, Disco: 0, Vea: 0 },
        quantity: 1
      }]);
    }
    setCustomItemText('');
    setSearchResults([]);
    setShowSearchDropdown(false);
  };

  // Real-time search with debounce
  const handleSearchInput = (value) => {
    setCustomItemText(value);
    if (searchDebounceRef.current) clearTimeout(searchDebounceRef.current);

    if (value.length < 2) {
      setSearchResults([]);
      setShowSearchDropdown(false);
      return;
    }

    setIsSearching(true);
    searchDebounceRef.current = setTimeout(() => {
      fetch(`http://localhost:5000/api/products/search?q=${encodeURIComponent(value)}&store=${encodeURIComponent(targetStore)}&limit=8`)
        .then(r => r.json())
        .then(data => {
          if (Array.isArray(data)) {
            setSearchResults(data);
            setShowSearchDropdown(data.length > 0);
          }
        })
        .catch(() => {})
        .finally(() => setIsSearching(false));
    }, 300);
  };

  const handleRemoveItem = (index) => {
    setCart(cart.filter((_, i) => i !== index));
  };

  const handleUpdateQuantity = (index, delta) => {
    setCart(cart.map((item, i) => {
      if (i === index) {
        const nq = item.quantity + delta;
        return nq > 0 ? { ...item, quantity: nq } : item;
      }
      return item;
    }));
  };

  const handleSelectVariant = (index, brandName) => {
    setCart(cart.map((item, i) => {
      if (i === index) {
        const catalogRef = PRODUCT_CATALOG.find(p => p.name === item.name);
        if (!catalogRef || !catalogRef.variants) return item;
        const matchedVariant = catalogRef.variants.find(v => v.brand === brandName);
        if (!matchedVariant) return item;

        // Re-calculate store prices based on variant factor
        const updatedPrices = {};
        Object.keys(catalogRef.basePrices).forEach(k => {
          updatedPrices[k] = Math.round(catalogRef.basePrices[k] * matchedVariant.factor);
        });

        return {
          ...item,
          selectedBrand: brandName,
          basePrices: updatedPrices
        };
      }
      return item;
    }));
  };

  // MATCHING ENGINE & OPTIMIZATION COMPUTATIONS
  const supermarkets = ['Carrefour', 'Dia', 'Coto', 'Jumbo', 'Disco', 'Vea'];

  const results = useMemo(() => {
    if (cart.length === 0) return null;

    // Calculate normal cost per supermarket without promos
    const baseTotals = {};
    supermarkets.forEach(store => {
      let sum = 0;
      cart.forEach(item => {
        sum += (item.basePrices[store] || 2000) * item.quantity;
      });
      baseTotals[store] = sum;
    });

    // Apply selected promos on simulated day
    const discountedTotals = {};
    const savingsAmount = {};

    supermarkets.forEach(store => {
      let base = baseTotals[store];
      let discountApplied = 0;

      // Look for user benefits applying to this store on simulated day (grouped structure has entries)
      selectedBenefits.forEach(benefit => {
        if (benefit.entries) {
          benefit.entries.forEach(entry => {
            // STRICT MATCH: Ensure the benefit is applied ONLY to the supermarket it specifies
            if (
              entry.supermercado.toLowerCase() === store.toLowerCase() &&
              entry.day.toLowerCase() === selectedDaySimulated.toLowerCase()
            ) {
              let rawDiscount = base * (entry.value / 100);
              if (rawDiscount > entry.limit) {
                rawDiscount = entry.limit;
              }
              discountApplied += rawDiscount;
            }
          });
        }
      });

      // Total with discount applied
      discountedTotals[store] = Math.max(base - discountApplied, 0);
      savingsAmount[store] = discountApplied;
    });

    // Find absolute best single store
    let bestSingleStore = supermarkets[0];
    supermarkets.forEach(store => {
      if (discountedTotals[store] < discountedTotals[bestSingleStore]) {
        bestSingleStore = store;
      }
    });

    // Worst single store to compare savings
    let worstSingleStore = supermarkets[0];
    supermarkets.forEach(store => {
      if (discountedTotals[store] > discountedTotals[worstSingleStore]) {
        worstSingleStore = store;
      }
    });

    const potentialSavings = discountedTotals[worstSingleStore] - discountedTotals[bestSingleStore];
    const efficiencyIndex = Math.round((discountedTotals[bestSingleStore] / baseTotals[bestSingleStore]) * 100);

    return {
      baseTotals,
      discountedTotals,
      savingsAmount,
      bestSingleStore,
      worstSingleStore,
      potentialSavings,
      efficiencyIndex
    };
  }, [cart, selectedBenefits, selectedDaySimulated]);


  // Dynamic Splits Builder based on cart and selected benefits
  const splitShoppingTrips = useMemo(() => {
    if (cart.length === 0) return [];

    // Group cart items into logical trips based on where their categories or stores are best discounted.
    // Let's create an assistant that proposes a split plan:
    // Trip 1: Fresh goods / Butcher on specific discount day (e.g. Wednesday with Cuenta DNI or Friday with Galicia)
    // Trip 2: Groceries (Almacén) on another optimal day.

    const trips = [];

    // Check if we have Coto or Carrefour items
    const cotoItems = cart.filter(item => item.basePrices.Coto !== undefined);
    const carrefourItems = cart.filter(item => item.basePrices.Carrefour !== undefined);
    const diaItems = cart.filter(item => item.basePrices.Dia !== undefined);

    if (cotoItems.length > 0) {
      trips.push({
        id: 1,
        store: 'Coto',
        suggestedDay: 'miércoles',
        reason: 'Ahorro Coto Club + promociones bancarias activas a mitad de semana.',
        items: cotoItems
      });
    }

    if (carrefourItems.length > 0 || diaItems.length > 0) {
      trips.push({
        id: 2,
        store: 'Carrefour / Dia',
        suggestedDay: 'miércoles',
        reason: 'Cuenta DNI activa (20% de reintegro en locales adheridos).',
        items: cart.filter(item => !cotoItems.includes(item))
      });
    }

    return trips.length > 0 ? trips : [{
      id: 1,
      store: 'Supermercado General',
      suggestedDay: 'miércoles',
      reason: 'Mayor densidad de promociones del mes.',
      items: cart
    }];
  }, [cart]);

  // Smart recommendation: only show when a meaningfully cheaper option exists
  const smartRecommendation = useMemo(() => {
    if (!results || cart.length === 0) return null;

    const currentBestCost = results.discountedTotals[results.bestSingleStore];
    const allDays = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo',
                     'mi\u00e9rcoles', 's\u00e1bado'];
    const allBenefits = Object.values(dynamicPromotions).flat();

    let best = null;
    let bestCost = currentBestCost;

    // Check every day x benefit combination for a cheaper option
    const allDaysNorm = ['lunes', 'martes', 'mi\u00e9rcoles', 'jueves', 'viernes', 's\u00e1bado', 'domingo'];
    allDaysNorm.forEach(day => {
      allBenefits.forEach(benefit => {
        benefit.entries.forEach(entry => {
          if (entry.day.toLowerCase() !== day) return;

          const store = entry.supermercado;
          const baseTotal = results.baseTotals[store];
          if (!baseTotal) return;

          let rawDiscount = baseTotal * (entry.value / 100);
          if (rawDiscount > entry.limit) rawDiscount = entry.limit;
          const discountedTotal = Math.max(baseTotal - rawDiscount, 0);

          if (discountedTotal < bestCost) {
            const isSameBenefit = selectedBenefits.some(b => b.id === benefit.id);
            bestCost = discountedTotal;
            best = {
              benefit,
              entry,
              day,
              store,
              cost: discountedTotal,
              savings: currentBestCost - discountedTotal,
              isSameBenefit
            };
          }
        });
      });
    });

    // Only surface if saving is meaningful (> $200)
    if (!best || best.savings < 200) return null;
    return best;
  }, [results, dynamicPromotions, selectedBenefits, selectedDaySimulated, cart]);

  return (
    <div className="app-layout">
      {/* HEADER SECTION (70% Editorial Premium) */}
      <header style={{ padding: '2rem 1.5rem 1rem', borderBottom: '1px solid var(--border-color)' }}>
        <span style={{ fontSize: '0.8rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--accent)', display: 'block', marginBottom: '0.5rem' }}>
          CompraIQ
        </span>
        <h1 style={{ fontSize: '2.25rem', fontFamily: 'var(--font-serif)', color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
          Planificá tu compra.
        </h1>
        <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)' }}>
          Te mostramos el mejor día, supermercado y medio de pago para ahorrar más.
        </p>
      </header>

      {/* TAB CONTENT */}
      <div style={{ flexGrow: 1, paddingBottom: '3.5rem' }}>

        {/* TAB 1: BENEFITS ONBOARDING */}
        {activeTab === 'benefits' && (
          <div className="step-container" style={{ maxWidth: '100%' }}>
            <h2 className="step-title">¿Dónde conviene comprar?</h2>
            <p className="step-subtitle">
              Compará tus descuentos por día y elegí el mejor momento.
            </p>

            {/* Carousel nav header: arrows aligned with day titles */}
            <div className="carousel-nav-header">
              <button
                type="button"
                className={`carousel-arrow prev ${carouselStartIdx === 0 ? 'arrow-hidden' : ''}`}
                onClick={() => setCarouselStartIdx(prev => Math.max(0, prev - 1))}
                aria-label="Anterior"
                disabled={carouselStartIdx === 0}
              >
                ‹
              </button>
              <div className="carousel-day-labels">
                {['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'].map((dayName, dayIdx) => {
                  const desktopStart = Math.min(4, carouselStartIdx);
                  const isDayActiveInDesktop = dayIdx >= desktopStart && dayIdx < desktopStart + 3;
                  const isDayActiveInMobile = dayIdx === carouselStartIdx;
                  if (typeof window !== 'undefined' && window.innerWidth < 768) {
                    if (!isDayActiveInMobile) return null;
                  } else {
                    if (!isDayActiveInDesktop) return null;
                  }
                  const displayDayName = dayName.charAt(0).toUpperCase() + dayName.slice(1);
                  return (
                    <span key={dayName} className="carousel-day-label-item">{displayDayName}</span>
                  );
                })}
              </div>
              <button
                type="button"
                className={`carousel-arrow next ${carouselStartIdx >= 4 ? 'arrow-hidden' : ''}`}
                onClick={() => setCarouselStartIdx(prev => prev + 1)}
                aria-label="Siguiente"
                disabled={carouselStartIdx >= 4}
              >
                ›
              </button>
            </div>

            {/* Columns scroll (no arrows inside) */}
            <div className="benefits-columns-scroll">
              {['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'].map((dayName, dayIdx) => {
                // Determine if day is active in mobile (shows only the selected single day)
                // and desktop (shows 3 days from carouselStartIdx)
                const isDayActiveInMobile = dayIdx === carouselStartIdx;

                // For desktop, clamp carouselStartIdx to max 4 to show exactly 3 columns (index 4, 5, 6)
                const desktopStart = Math.min(4, carouselStartIdx);
                const isDayActiveInDesktop = dayIdx >= desktopStart && dayIdx < desktopStart + 3;

                // Gather all promotions (flat) for this day
                const dayPromos = [];
                Object.keys(dynamicPromotions).forEach(cat => {
                  dynamicPromotions[cat].forEach(benefit => {
                    benefit.entries.forEach(entry => {
                      if (entry.day.toLowerCase() === dayName.toLowerCase()) {
                        dayPromos.push({
                          id: `${benefit.id}-${entry.supermercado}-${entry.day}`,
                          parentBenefit: benefit,
                          name: benefit.name,
                          supermercado: entry.supermercado,
                          value: entry.value,
                          limit: entry.limit
                        });
                      }
                    });
                  });
                });

                // Sort promos descending by value
                dayPromos.sort((a, b) => b.value - a.value);

                const displayDayName = dayName.charAt(0).toUpperCase() + dayName.slice(1);

                return (
                  <div
                    key={dayName}
                    className={`redesigned-week-day-column day-${dayName} ${isDayActiveInMobile ? 'active-column' : ''} ${isDayActiveInDesktop ? 'visible-in-carousel' : ''}`}
                  >

                    <div className="column-promos-list">
                      {dayPromos.length > 0 ? (
                        dayPromos.map((p) => {
                          const isSel = selectedBenefits.some(b => b.id === p.parentBenefit.id);
                          const benImg = getBenefitImage(p.name);
                          const superImg = getSupermarketImage(p.supermercado);

                          let bankName = p.name;
                          let cardName = p.parentBenefit.subName || '';

                          return (
                            <div
                              key={p.id}
                              className={`visual-day-promo-card-redesigned ${isSel ? 'selected' : ''}`}
                              onClick={() => handleToggleBenefit(p.parentBenefit)}
                              title={`${p.name} - ${p.value}% en ${p.supermercado}`}
                            >
                              {/* Selected check indicator */}
                              <div className={`redesigned-check-indicator ${isSel ? 'active' : ''}`}>
                                {isSel && <Check style={{ width: '10px', height: '10px', color: '#fff' }} />}
                              </div>

                              {/* Supermarket Logo */}
                              <div className="card-super-logo">
                                {p.supermercado.toLowerCase() === 'dia' ? (
                                  <span className="dia-logo-placeholder">DIA %</span>
                                ) : superImg ? (
                                  <img src={superImg} alt={p.supermercado} />
                                ) : (
                                  <span className="card-super-text-logo">{p.supermercado}</span>
                                )}
                              </div>

                              {/* Discount Value */}
                              <div className="card-discount-val">{p.value}% OFF</div>

                              {/* Bank / Card info */}
                              <div className="card-bank-info">
                                <span className="bank-name">{bankName}</span>
                                {cardName && <span className="card-name">{cardName}</span>}
                              </div>
                            </div>
                          );
                        })
                      ) : (
                        <div className="no-promos-text">Sin promos</div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {selectedBenefits.length > 0 && (
              <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <button className="btn-text btn-danger-text" onClick={handleClearBenefits}>
                  Limpiar selección
                </button>
                <button
                  className="btn"
                  onClick={() => setActiveTab('cart')}
                  style={{ backgroundColor: 'var(--accent)', color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.6rem 1.2rem', borderRadius: '4px' }}
                >
                  Ir al Changuito <ChevronRight style={{ width: '16px', height: '16px' }} />
                </button>
              </div>
            )}
          </div>
        )}

        {/* TAB 3: SHOPPING CART & OPTIMIZER */}
        {activeTab === 'cart' && (
          <div className="step-container">
            <h2 className="step-title" style={{ fontFamily: 'var(--font-serif)' }}>¿Qué necesitás comprar?</h2>

            {/* Real product search with dropdown */}
            <div style={{ position: 'relative' }}>
              <form onSubmit={handleAddCustomItem}>
                <div className="cart-input-wrapper">
                  <ShoppingBag className="cart-input-icon" />
                  <input
                    type="text"
                    className="cart-input"
                    placeholder={`Buscar en ${targetStore}...`}
                    value={customItemText}
                    onChange={(e) => handleSearchInput(e.target.value)}
                    onFocus={() => searchResults.length > 0 && setShowSearchDropdown(true)}
                    onBlur={() => setTimeout(() => setShowSearchDropdown(false), 150)}
                    autoComplete="off"
                  />
                  <button
                    type="submit"
                    style={{ position: 'absolute', right: '0.5rem', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--accent)', cursor: 'pointer', padding: '0.5rem' }}
                  >
                    {isSearching
                      ? <span style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>...</span>
                      : <Plus style={{ width: '20px', height: '20px' }} />
                    }
                  </button>
                </div>
              </form>

              {/* Search results dropdown */}
              {showSearchDropdown && searchResults.length > 0 && (
                <div style={{
                  position: 'absolute', top: '100%', left: 0, right: 0, zIndex: 100,
                  background: '#fff', border: '1px solid var(--border-color)',
                  borderRadius: '12px', boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
                  maxHeight: '280px', overflowY: 'auto', marginTop: '4px'
                }}>
                  {searchResults.map((product) => {
                    const priceAtStore = product.prices[targetStore];
                    const minPrice = Math.min(...Object.values(product.prices));
                    const alreadyInCart = cart.some(c => c.product_id === product.product_id || c.name === product.nombre);
                    return (
                      <div
                        key={product.product_id}
                        onClick={() => {
                          if (!alreadyInCart) handleAddItem(product);
                          setCustomItemText('');
                          setSearchResults([]);
                          setShowSearchDropdown(false);
                        }}
                        style={{
                          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                          padding: '0.65rem 1rem', cursor: alreadyInCart ? 'default' : 'pointer',
                          borderBottom: '1px solid var(--border-color)',
                          opacity: alreadyInCart ? 0.5 : 1,
                          transition: 'background 0.15s'
                        }}
                        onMouseEnter={e => { if (!alreadyInCart) e.currentTarget.style.background = '#f8f9fa'; }}
                        onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
                      >
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {product.nombre}
                          </div>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)', marginTop: '1px' }}>
                            {product.categoria} {product.presentacion ? `· ${product.presentacion}` : ''}
                          </div>
                        </div>
                        <div style={{ textAlign: 'right', flexShrink: 0, marginLeft: '0.75rem' }}>
                          {priceAtStore ? (
                            <span style={{ fontSize: '0.9rem', fontWeight: '800', color: 'var(--accent)' }}>
                              ${fmt(priceAtStore)}
                            </span>
                          ) : (
                            <span style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)' }}>
                              desde ${fmt(minPrice)}
                            </span>
                          )}
                          <div style={{ fontSize: '0.65rem', color: 'var(--text-tertiary)' }}>
                            {priceAtStore ? targetStore : 'otro super'}
                          </div>
                        </div>
                        {alreadyInCart && (
                          <span style={{ marginLeft: '0.5rem', fontSize: '0.65rem', background: '#dcfce7', color: '#16a34a', padding: '2px 6px', borderRadius: '10px', fontWeight: '700' }}>
                            En carrito
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Quick Add Pills — real products from the selected store */}
            {popularProducts.length > 0 && (
              <div className="quick-add-pills">
                {popularProducts
                  .filter(p => !cart.some(c => c.product_id === p.product_id || c.name === p.nombre))
                  .slice(0, 5)
                  .map((p) => (
                    <div key={p.product_id} className="pill" onClick={() => handleAddItem(p)}>
                      + {p.nombre.split(' ').slice(0, 3).join(' ')}
                    </div>
                  ))
                }
              </div>
            )}

            {/* Shopping List */}
            {cart.length > 0 ? (
              <div className="shopping-list">
                {cart.map((item, idx) => {
                  const allPrices = Object.values(item.basePrices).filter(v => v > 0);
                  const lowestPrice = allPrices.length > 0 ? Math.min(...allPrices) : 0;
                  const itemPrice = item.basePrices[targetStore] || lowestPrice;
                  const itemSubtotal = itemPrice * item.quantity;

                  return (
                    <div
                      className="shopping-item"
                      key={idx}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '0.85rem 1rem',
                        border: '1px solid var(--border-color)',
                        borderRadius: '12px',
                        marginBottom: '0.5rem',
                        backgroundColor: '#fff',
                        boxShadow: '0 2px 6px rgba(0,0,0,0.02)'
                      }}
                    >
                      <div className="item-left" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexGrow: 1 }}>
                        <div className="checkbox-custom checked" style={{ borderRadius: '50%' }}>
                          <Check style={{ width: '10px', height: '10px' }} />
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                          <span className="item-name" style={{ fontSize: '0.95rem', fontWeight: '600' }}>
                            {item.name}
                          </span>
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                            {item.presentacion || item.categoria || 'Producto'}{itemPrice > 0 ? ` · $${fmt(itemPrice)} c/u en ${targetStore}` : ' · precio a confirmar'}
                          </span>
                        </div>
                      </div>

                      {/* Brand selector setting button + quantity controls */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                        <div style={{ textAlign: 'right', minWidth: '70px', marginRight: '0.25rem' }}>
                          <span style={{ fontSize: '0.9rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                            ${fmt(itemSubtotal)}
                          </span>
                        </div>



                        <div style={{ display: 'flex', alignItems: 'center', border: '1px solid var(--border-color)', borderRadius: '6px', overflow: 'hidden', height: '28px' }}>
                          <button
                            onClick={() => handleUpdateQuantity(idx, -1)}
                            style={{ background: 'none', border: 'none', width: '24px', height: '100%', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                          >
                            -
                          </button>
                          <span style={{ fontSize: '0.8rem', fontWeight: '700', padding: '0 8px', backgroundColor: 'var(--bg-secondary)', height: '100%', display: 'flex', alignItems: 'center' }}>
                            ({item.quantity})
                          </span>
                          <button
                            onClick={() => handleUpdateQuantity(idx, 1)}
                            style={{ background: 'none', border: 'none', width: '24px', height: '100%', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                          >
                            +
                          </button>
                        </div>

                        <button
                          onClick={() => handleRemoveItem(idx)}
                          style={{ background: 'none', border: 'none', color: 'var(--text-tertiary)', cursor: 'pointer', padding: '0.25rem' }}
                        >
                          <Trash2 style={{ width: '15px', height: '15px' }} />
                        </button>
                      </div>
                    </div>
                  );
                })}

                {/* Totals row — simplified, no redundant store name */}
                {(() => {
                  const totalValue = Math.round(results?.baseTotals[targetStore] || 0);
                  return (
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '0.75rem 0',
                      borderTop: '1px solid var(--border-color)',
                      marginTop: '0.75rem',
                    }}>
                      <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: '500' }}>
                        Total &middot; {cart.reduce((s, i) => s + i.quantity, 0)} productos
                      </span>
                      <span style={{ fontSize: '1.3rem', fontWeight: '800', color: 'var(--text-primary)', fontFamily: 'var(--font-serif)' }}>
                        <AnimatedTotal value={totalValue} />
                      </span>
                    </div>
                  );
                })()}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '3rem 1.5rem', color: 'var(--text-tertiary)' }}>
                <ShoppingBag style={{ width: '40px', height: '40px', margin: '0 auto 1rem', display: 'block' }} />
                Tu changuito está vacío. Agregá productos arriba.
              </div>
            )}

            {/* Matching Engine Suggestions & Metrics */}
            {results && (
              <div className="optimization-section">

                {/* Savings Hero Banner */}
                {results.savingsAmount[results.bestSingleStore] > 0 && (
                  <div style={{
                    background: 'linear-gradient(135deg, #16a34a 0%, #15803d 100%)',
                    borderRadius: '16px',
                    padding: '1.5rem',
                    marginBottom: '1rem',
                    textAlign: 'center',
                    boxShadow: '0 4px 20px rgba(22, 163, 74, 0.25)'
                  }}>
                    <p style={{
                      fontSize: '0.8rem',
                      color: 'rgba(255,255,255,0.8)',
                      textTransform: 'uppercase',
                      letterSpacing: '0.1em',
                      fontWeight: '600',
                      marginBottom: '0.35rem'
                    }}>
                      Con tus beneficios, ahorrás
                    </p>
                    <p style={{
                      fontSize: '2.5rem',
                      fontFamily: 'var(--font-serif)',
                      fontWeight: '800',
                      color: '#ffffff',
                      lineHeight: 1.1,
                      marginBottom: '0.25rem'
                    }}>
                      ${fmt(results.savingsAmount[results.bestSingleStore])}
                    </p>
                    <p style={{
                      fontSize: '0.85rem',
                      color: 'rgba(255,255,255,0.75)',
                    }}>
                      comprando en <strong style={{ color: '#fff' }}>{results.bestSingleStore}</strong>
                    </p>
                  </div>
                )}

                {/* Price cards: base vs discounted */}
                <div className="financial-overview">
                  <div className="financial-card">
                    <span className="financial-label">Precio sin descuento</span>
                    <span className="financial-value" style={{ textDecoration: 'line-through', color: 'var(--text-tertiary)' }}>${fmt(results.baseTotals[results.bestSingleStore])}</span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>{cart.reduce((s, i) => s + i.quantity, 0)} productos</span>
                  </div>
                  <div className="financial-card" style={{ borderColor: '#16a34a' }}>
                    <span className="financial-label">Pagás con descuento</span>
                    <span className="financial-value" style={{ color: '#16a34a' }}>${fmt(results.discountedTotals[results.bestSingleStore])}</span>
                    <span style={{ fontSize: '0.75rem', color: '#16a34a', fontWeight: '600' }}>en {results.bestSingleStore}</span>
                  </div>
                </div>

                {/* Single Store Rank Card - Information Cartography */}
                <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem', fontFamily: 'var(--font-serif)' }}>Comparación de Canasta</h3>
                <div className="store-comparison-list">
                  {(() => {
                    // Sort stores by discounted total ascending (cheapest first)
                    const sortedStores = [...supermarkets].sort((a, b) =>
                      (results.discountedTotals[a] ?? Infinity) - (results.discountedTotals[b] ?? Infinity)
                    );
                    const visibleStores = showAllStores ? sortedStores : sortedStores.slice(0, 3);

                    return (
                      <>
                        {visibleStores.map((store, rank) => {
                          const isBest = store === results.bestSingleStore;
                          const storeLower = store.toLowerCase();

                          // Logo logic — Dia has no SVG, use placeholder div
                          let logoEl = null;
                          if (storeLower === 'dia') {
                            logoEl = (
                              <span style={{
                                display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                                width: '28px', height: '28px', borderRadius: '4px',
                                backgroundColor: '#EE1C25', color: '#fff',
                                fontSize: '0.55rem', fontWeight: '900', letterSpacing: '-0.5px',
                                flexShrink: 0
                              }}>DIA</span>
                            );
                          } else {
                            const logoMap = {
                              coto: '/visuales/spk_assets/coto.webp',
                              carrefour: '/visuales/spk_assets/carrefour.svg',
                              jumbo: '/visuales/spk_assets/jumbo.svg',
                              disco: '/visuales/spk_assets/disco.svg',
                              vea: '/visuales/spk_assets/vea.webp',
                            };
                            const src = logoMap[storeLower];
                            logoEl = src
                              ? <img src={src} alt={store} style={{ width: '28px', height: '28px', objectFit: 'contain', flexShrink: 0 }} />
                              : <span style={{ width: '28px', height: '28px', borderRadius: '50%', backgroundColor: 'var(--border-color)', flexShrink: 0, display: 'inline-block' }} />;
                          }

                          return (
                            <div
                              key={store}
                              className={`store-comparison-row ${isBest ? 'best' : ''}`}
                              style={{
                                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                                padding: '0.6rem 0', borderBottom: '1px solid var(--border-color)'
                              }}
                            >
                              <span style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                {rank === 0 && <span style={{ fontSize: '0.85rem' }}>🥇</span>}
                                {rank === 1 && <span style={{ fontSize: '0.85rem' }}>🥈</span>}
                                {rank === 2 && <span style={{ fontSize: '0.85rem' }}>🥉</span>}
                                {rank > 2 && <span style={{ width: '1.1rem', display: 'inline-block' }} />}
                                {logoEl}
                                <span style={{ fontWeight: isBest ? '700' : 'normal', color: isBest ? 'var(--accent)' : 'inherit' }}>
                                  {store} {isBest && '(Mejor Opción)'}
                                </span>
                              </span>
                              <span style={{ fontWeight: isBest ? '700' : 'normal', color: isBest ? 'var(--accent)' : 'inherit' }}>
                                ${fmt(results.discountedTotals[store])}
                                {results.savingsAmount[store] > 0 && (
                                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginLeft: '0.5rem' }}>
                                    (-${fmt(results.savingsAmount[store])})
                                  </span>
                                )}
                              </span>
                            </div>
                          );
                        })}

                        {/* Show more / collapse toggle */}
                        {sortedStores.length > 3 && (
                          <button
                            onClick={() => setShowAllStores(v => !v)}
                            style={{
                              display: 'block', width: '100%', textAlign: 'center',
                              padding: '0.5rem', marginTop: '0.25rem',
                              border: 'none', background: 'none', cursor: 'pointer',
                              fontSize: '0.8rem', color: 'var(--accent)', fontWeight: '600'
                            }}
                          >
                            {showAllStores ? '▲ Ver menos' : `▼ Ver ${sortedStores.length - 3} más`}
                          </button>
                        )}
                      </>
                    );
                  })()}
                </div>

                {/* Smart Recommendation -- only shows when a cheaper option exists */}
                {smartRecommendation && (
                  <>
                    <h3 style={{ fontSize: '1.15rem', marginTop: '1rem', marginBottom: '0.5rem', fontFamily: 'var(--font-serif)' }}>
                      Podés ahorrar más
                    </h3>
                    <div style={{
                      background: 'linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)',
                      border: '1.5px solid #f59e0b',
                      borderRadius: '14px',
                      padding: '1rem 1.25rem',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.6rem'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <span style={{
                          fontSize: '1.8rem',
                          fontFamily: 'var(--font-serif)',
                          fontWeight: '900',
                          color: '#b45309'
                        }}>
                          ${fmt(smartRecommendation.savings)}
                        </span>
                        <span style={{ fontSize: '0.8rem', color: '#78350f', fontWeight: '600', lineHeight: 1.3 }}>
                          más barato<br/>cambiando de opción
                        </span>
                      </div>

                      <p style={{ fontSize: '0.85rem', color: '#78350f', margin: 0, lineHeight: 1.5 }}>
                        {smartRecommendation.isSameBenefit ? (
                          <>
                            Con tu mismo beneficio <strong>{smartRecommendation.benefit.name}</strong>,
                            comprando el <strong>{smartRecommendation.day}</strong> en <strong>{smartRecommendation.store}</strong>,
                            pagás <strong>${fmt(smartRecommendation.cost)}</strong> en vez de <strong>${fmt(results.discountedTotals[results.bestSingleStore])}</strong>.
                          </>
                        ) : (
                          <>
                            Usando <strong>{smartRecommendation.benefit.name}</strong> ({smartRecommendation.entry.value}% OFF)
                            el <strong>{smartRecommendation.day}</strong> en <strong>{smartRecommendation.store}</strong>,
                            pagás <strong>${fmt(smartRecommendation.cost)}</strong> en vez de <strong>${fmt(results.discountedTotals[results.bestSingleStore])}</strong>.
                          </>
                        )}
                      </p>

                      <span style={{
                        alignSelf: 'flex-start',
                        fontSize: '0.65rem',
                        fontWeight: '700',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                        background: smartRecommendation.isSameBenefit ? '#d1fae5' : '#dbeafe',
                        color: smartRecommendation.isSameBenefit ? '#065f46' : '#1e40af',
                        padding: '3px 10px',
                        borderRadius: '20px'
                      }}>
                        {smartRecommendation.isSameBenefit ? 'Mismo beneficio, otro dia' : 'Beneficio diferente'}
                      </span>
                    </div>
                  </>
                )}

                {/* SPLIT SHOPPING TRIP PLANNER */}
                <div style={{ marginTop: '1.5rem', borderTop: '1px solid var(--border-color)', paddingTop: '1.25rem' }}>
                  <h3 style={{ fontSize: '1.15rem', fontFamily: 'var(--font-serif)', marginBottom: '0.5rem' }}>
                    Asistente de Compra en Varios Viajes
                  </h3>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                    Dividí tu changuito para maximizar tus ahorros de acuerdo a los beneficios que tenés cargados.
                  </p>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {splitShoppingTrips.map((trip, idx) => (
                      <div
                        key={idx}
                        className="combo-banner"
                        style={{
                          backgroundColor: '#fff',
                          border: '1px solid var(--border-color)',
                          display: 'flex',
                          flexDirection: 'column',
                          gap: '0.5rem',
                          padding: '1rem'
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.8rem', fontWeight: 'bold', textTransform: 'uppercase', color: 'var(--accent)' }}>
                            Viaje {idx + 1}: Comprar en {trip.store}
                          </span>
                          <span className="badge" style={{ backgroundColor: 'var(--accent-light)', color: 'var(--accent)', fontSize: '0.7rem' }}>
                            Sugerido: {trip.suggestedDay}
                          </span>
                        </div>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: 0 }}>
                          {trip.reason}
                        </p>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem', marginTop: '0.25rem' }}>
                          {trip.items.map((item, itemIdx) => (
                            <span key={itemIdx} className="super-text-badge" style={{ fontSize: '0.65rem', background: '#f1f3f5', border: '1px solid var(--border-color)', borderRadius: '4px', textTransform: 'none' }}>
                              {item.name} ({item.quantity})
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            )}

          </div>
        )}

      </div>

      {/* FOOTER BAR (Apple Style minimal) */}
      <footer className="app-footer-nav">
        <button
          className={`footer-nav-btn ${activeTab === 'benefits' ? 'active' : ''}`}
          onClick={() => { setActiveTab('benefits'); setSelectedCategory(null); }}
        >
          <CreditCard style={{ width: '20px', height: '20px' }} />
          <span>Beneficios</span>
        </button>
        <button
          className={`footer-nav-btn ${activeTab === 'cart' ? 'active' : ''}`}
          onClick={() => setActiveTab('cart')}
        >
          <ShoppingBag style={{ width: '20px', height: '20px' }} />
          <span>Changuito</span>
        </button>
      </footer>

      {/* BRAND / PRODUCT SELECTION HIGH-FIDELITY MODAL */}
      {activeModalItemIndex !== null && (() => {
        const item = cart[activeModalItemIndex];
        const catalogItem = PRODUCT_CATALOG.find(p => p.name === item.name);
        if (!catalogItem || !catalogItem.variants) return null;

        // Determine which supermarket we are shopping at (from selected benefits)
        // If a benefit is selected, use its supermarket, otherwise fallback to the best single store or a default
        const targetStore = (selectedBenefits.length > 0 && selectedBenefits[0].entries && selectedBenefits[0].entries[0]?.supermercado)
          || results?.bestSingleStore
          || 'Carrefour';

        // Build per-brand price at target store, sorted cheapest first
        const brandsForTargetStore = catalogItem.variants
          .map(v => ({
            brand: v.brand,
            factor: v.factor,
            price: targetStore ? Math.round((catalogItem.basePrices[targetStore] || 2000) * v.factor) : null
          }))
          .sort((a, b) => (a.price || 0) - (b.price || 0));

        // Build per-store cheapest brand for "other supermarkets" section
        const otherStores = supermarkets
          .filter(s => s !== targetStore)
          .map(store => {
            // find cheapest brand for this store
            const cheapestBrand = catalogItem.variants
              .map(v => ({ brand: v.brand, price: Math.round((catalogItem.basePrices[store] || 2000) * v.factor) }))
              .sort((a, b) => a.price - b.price)[0];
            return { store, cheapestBrand };
          })
          .sort((a, b) => a.cheapestBrand.price - b.cheapestBrand.price);

        return (
          <div className="premium-modal-overlay" onClick={() => setActiveModalItemIndex(null)}>
            <div className="premium-modal-content" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <h3>Elegí la Marca</h3>
                <button className="modal-close-btn" onClick={() => setActiveModalItemIndex(null)}>×</button>
              </div>
              <p className="modal-subtitle">
                Precios para <strong>{item.name}</strong>
                {targetStore && <span> en <strong style={{ color: 'var(--accent)' }}>{targetStore}</strong></span>}.
              </p>

              <div className="brand-cards-grid">
                {/* ── TARGET STORE BRANDS ── */}
                {targetStore && brandsForTargetStore.map((b, vIdx) => {
                  const isSelected = item.selectedBrand === b.brand;
                  const variant = catalogItem.variants.find(v => v.brand === b.brand);
                  const isCheapest = vIdx === 0;

                  return (
                    <div
                      key={vIdx}
                      className={`brand-modal-card ${isSelected ? 'selected' : ''}`}
                      onClick={() => {
                        handleSelectVariant(activeModalItemIndex, b.brand);
                        setActiveModalItemIndex(null);
                      }}
                    >
                      <div className="brand-modal-card-header">
                        <span className="brand-title">
                          {isCheapest && <span style={{ color: '#22c55e', marginRight: '4px', fontSize: '0.75rem' }}>★</span>}
                          {b.brand}
                        </span>
                        <span style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                          {isCheapest && <span style={{ fontSize: '0.65rem', background: '#dcfce7', color: '#16a34a', padding: '1px 6px', borderRadius: '4px', fontWeight: '700' }}>MÁS BARATO</span>}
                          <span className={`brand-percentage ${variant && variant.factor >= 1 ? 'increase' : 'decrease'}`}>
                            {variant && variant.factor >= 1 ? `+${Math.round((variant.factor - 1) * 100)}%` : variant ? `-${Math.round((1 - variant.factor) * 100)}%` : ''}
                          </span>
                        </span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '2px' }}>
                        <span style={{ fontSize: '1.1rem', fontWeight: '800', color: isSelected ? 'var(--accent)' : 'var(--text-primary)', fontFamily: 'var(--font-serif)' }}>
                          ${fmt(b.price)}
                        </span>
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>en {targetStore}</span>
                      </div>
                    </div>
                  );
                })}

                {/* ── SEPARATOR: OTROS SUPERMERCADOS ── */}
                {otherStores.length > 0 && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: '0.5rem 0 0.25rem' }}>
                    <div style={{ flex: 1, height: '1px', background: 'var(--border-color)' }} />
                    <span style={{ fontSize: '0.65rem', color: 'var(--text-tertiary)', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.08em', whiteSpace: 'nowrap' }}>
                      Otros supermercados (referencia)
                    </span>
                    <div style={{ flex: 1, height: '1px', background: 'var(--border-color)' }} />
                  </div>
                )}

                {/* ── OTHER STORES (sorted cheapest first, not clickable) ── */}
                {otherStores.map((s, sIdx) => {
                  const storeLogoSrc = getSupermarketImage(s.store);
                  const isCheapestStore = sIdx === 0;

                  return (
                    <div
                      key={s.store}
                      className="brand-modal-card"
                      style={{ opacity: 0.8, cursor: 'default', borderStyle: 'dashed' }}
                    >
                      <div className="brand-modal-card-header">
                        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          {storeLogoSrc
                            ? <img src={storeLogoSrc} alt={s.store} style={{ height: '16px', width: 'auto', objectFit: 'contain' }} />
                            : <span className="brand-title" style={{ fontSize: '0.8rem' }}>{s.store}</span>
                          }
                          {storeLogoSrc && <span className="brand-title" style={{ fontSize: '0.8rem' }}>{s.store}</span>}
                        </span>
                        {isCheapestStore && (
                          <span style={{ fontSize: '0.65rem', background: '#f0f9ff', color: '#0284c7', padding: '1px 6px', borderRadius: '4px', fontWeight: '700' }}>MÁS BARATO</span>
                        )}
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '2px' }}>
                        <span style={{ fontSize: '0.95rem', fontWeight: '700', color: 'var(--text-secondary)', fontFamily: 'var(--font-serif)' }}>
                          ${fmt(s.cheapestBrand.price)}
                        </span>
                        <span style={{ fontSize: '0.65rem', color: 'var(--text-tertiary)' }}>{s.cheapestBrand.brand}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        );
      })()}
    </div>
  );
}
