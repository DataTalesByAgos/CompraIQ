import React, { useState, useMemo } from 'react';
import {
  CreditCard,
  Building2,
  Wallet,
  Calendar,
  ShoppingBag,
  Sparkles,
  Check,
  ChevronRight,
  Trash2,
  Plus,
  TrendingDown,
  DollarSign,
  Maximize2,
  Info,
  CalendarDays,
  Eye
} from 'lucide-react';

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
  const [calendarFilter, setCalendarFilter] = useState('my'); // 'my' (selected benefits) or 'all' (all database promos)
  const [activeModalItemIndex, setActiveModalItemIndex] = useState(null); // Track item variant modal state

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

  // Add Item to cart
  const handleAddItem = (catalogItem) => {
    const exists = cart.find(item => item.name === catalogItem.name);
    if (exists) {
      setCart(cart.map(item => item.name === catalogItem.name ? { ...item, quantity: item.quantity + 1 } : item));
    } else {
      // Add default brand factor
      const defaultVariant = catalogItem.variants ? catalogItem.variants[0] : null;
      const basePricesCopy = { ...catalogItem.basePrices };
      if (defaultVariant) {
        Object.keys(basePricesCopy).forEach(k => {
          basePricesCopy[k] = Math.round(basePricesCopy[k] * defaultVariant.factor);
        });
      }
      setCart([...cart, {
        ...catalogItem,
        selectedBrand: defaultVariant ? defaultVariant.brand : 'Genérico',
        basePrices: basePricesCopy,
        quantity: 1
      }]);
    }
  };

  const handleAddCustomItem = (e) => {
    e.preventDefault();
    if (!customItemText.trim()) return;

    // Check if matched in catalog
    const matched = PRODUCT_CATALOG.find(p => p.name.toLowerCase().includes(customItemText.toLowerCase()));
    if (matched) {
      handleAddItem(matched);
    } else {
      // Create dynamic fallback item
      const dynamicPrices = {
        Carrefour: 2500, Dia: 2400, Coto: 2450, Jumbo: 2600, Disco: 2600, Vea: 2520
      };
      setCart([...cart, { name: customItemText, category: 'Almacén', basePrices: dynamicPrices, quantity: 1 }]);
    }
    setCustomItemText('');
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

  // Calendar helper – Calculates dynamic current month and year automatically
  const calendarMonthData = useMemo(() => {
    const today = new Date();
    const year = today.getFullYear();
    const monthIndex = today.getMonth(); // 0-11

    // Month names array in Spanish
    const monthNames = [
      'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];
    const monthName = `${monthNames[monthIndex]} ${year}`;

    // Calculate total days in current month
    const daysInMonth = new Date(year, monthIndex + 1, 0).getDate();

    const weekdaysOrder = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'];

    const flatPromos = [];
    Object.keys(dynamicPromotions).forEach(cat => {
      dynamicPromotions[cat].forEach(benefit => {
        const isSelectedBenefit = selectedBenefits.some(sb => sb.id === benefit.id);
        if (calendarFilter === 'all' || isSelectedBenefit) {
          benefit.entries.forEach(entry => {
            flatPromos.push({
              parentBenefit: benefit,
              name: benefit.name,
              supermercado: entry.supermercado,
              day: entry.day.toLowerCase(),
              value: entry.value,
              limit: entry.limit
            });
          });
        }
      });
    });

    const days = [];
    for (let dayNum = 1; dayNum <= daysInMonth; dayNum++) {
      const date = new Date(year, monthIndex, dayNum);
      let dayOfWeekIndex = date.getDay() - 1;
      if (dayOfWeekIndex === -1) dayOfWeekIndex = 6;
      const dayName = weekdaysOrder[dayOfWeekIndex];

      const activePromos = flatPromos.filter(p => p.day === dayName);

      days.push({
        dayNum,
        dayName,
        dateString: `${year}-${String(monthIndex + 1).padStart(2, '0')}-${String(dayNum).padStart(2, '0')}`,
        promos: activePromos,
        hasPromo: activePromos.length > 0
      });
    }

    return {
      monthName,
      days,
      year,
      monthIndex
    };
  }, [dynamicPromotions, selectedBenefits, calendarFilter]);

  // Selected calendar day detail state
  const [selectedCalendarDayNum, setSelectedCalendarDayNum] = useState(new Date().getDate());
  const selectedDayInfo = useMemo(() => {
    return calendarMonthData.days.find(d => d.dayNum === selectedCalendarDayNum) || calendarMonthData.days[0];
  }, [calendarMonthData, selectedCalendarDayNum]);

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
          <div className="step-container">
            <h2 className="step-title">¿Con qué beneficios contás?</h2>
            <p className="step-subtitle">
              Seleccioná tus tarjetas, bancos o membresías de clubes para encontrar descuentos acumulables en supermercados.
            </p>

            {/* 5-COLUMN WEEK LAYOUT FOR BENEFITS */}
            <div className="benefits-week-grid">
              {['lunes', 'martes', 'miércoles', 'jueves', 'viernes'].map(dayName => {
                // Gather all promotions (flat) for this day
                const dayPromos = [];
                Object.keys(dynamicPromotions).forEach(cat => {
                  dynamicPromotions[cat].forEach(benefit => {
                    benefit.entries.forEach(entry => {
                      if (entry.day.toLowerCase() === dayName.toLowerCase()) {
                        dayPromos.push({
                          id: `${benefit.id}-${entry.supermercado}-${entry.day}`,
                          parentBenefit: benefit, // keep reference for selection toggling
                          name: benefit.name,
                          supermercado: entry.supermercado,
                          value: entry.value,
                          limit: entry.limit
                        });
                      }
                    });
                  });
                });

                return (
                  <div key={dayName} className="week-day-column">
                    <div className="week-day-header">
                      {dayName.charAt(0).toUpperCase() + dayName.slice(1, 3)}
                    </div>
                    <div className="week-day-promos-container">
                      {dayPromos.length > 0 ? (
                        dayPromos.map(p => {
                          const isSel = selectedBenefits.some(b => b.id === p.parentBenefit.id);
                          const benImg = getBenefitImage(p.name);
                          const superImg = getSupermarketImage(p.supermercado);

                          return (
                            <div
                              key={p.id}
                              className={`visual-day-promo-card ${isSel ? 'selected' : ''}`}
                              onClick={() => handleToggleBenefit(p.parentBenefit)}
                              title={`${p.name} - ${p.value}% en ${p.supermercado}`}
                            >
                              {/* Selected mini check */}
                              <div className={`mini-check ${isSel ? 'active' : ''}`}>
                                {isSel && <Check style={{ width: '6px', height: '6px', color: '#fff' }} />}
                              </div>

                              {/* Benefit Logo */}
                              <div className="promo-mini-logo">
                                {benImg ? (
                                  <img src={benImg} alt={p.name} />
                                ) : (
                                  <span>{p.name.slice(0, 2).toUpperCase()}</span>
                                )}
                              </div>

                              {/* Discount Value */}
                              <div className="promo-mini-value">{p.value}%</div>

                              {/* Supermarket Logo */}
                              <div className="promo-mini-super">
                                {superImg ? (
                                  <img src={superImg} alt={p.supermercado} />
                                ) : (
                                  <span className="super-mini-txt">{p.supermercado.slice(0, 3)}</span>
                                )}
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
                  onClick={() => setActiveTab('calendar')}
                  style={{ backgroundColor: 'var(--accent)', color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.6rem 1.2rem', borderRadius: '4px' }}
                >
                  Ver Calendario <ChevronRight style={{ width: '16px', height: '16px' }} />
                </button>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: SMART CALENDAR */}
        {activeTab === 'calendar' && (
          <div className="step-container">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
              <h2 className="step-title" style={{ margin: 0 }}>{calendarMonthData.monthName}</h2>
              {/* Ojo / Filter pills */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', border: '1px solid var(--border-color)', padding: '2px', borderRadius: '20px', backgroundColor: 'var(--bg-secondary)' }}>
                <button
                  onClick={() => setCalendarFilter('all')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    border: 'none',
                    borderRadius: '20px',
                    padding: '4px 10px',
                    fontSize: '0.75rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    backgroundColor: calendarFilter === 'all' ? 'var(--accent)' : 'transparent',
                    color: calendarFilter === 'all' ? '#fff' : 'var(--text-secondary)'
                  }}
                >
                  <Eye style={{ width: '12px', height: '12px' }} /> Ver Todos
                </button>
                <button
                  onClick={() => setCalendarFilter('my')}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    border: 'none',
                    borderRadius: '20px',
                    padding: '4px 10px',
                    fontSize: '0.75rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    backgroundColor: calendarFilter === 'my' ? 'var(--accent)' : 'transparent',
                    color: calendarFilter === 'my' ? '#fff' : 'var(--text-secondary)'
                  }}
                >
                  Mis Beneficios
                </button>
              </div>
            </div>
            <p className="step-subtitle">
              Seleccioná un día del mes para ver sus descuentos activos y planificar tus viajes de compra.
            </p>

            <div className="calendar-container">
              <div className="calendar-grid">
                <span className="calendar-day-header">Lun</span>
                <span className="calendar-day-header">Mar</span>
                <span className="calendar-day-header">Mié</span>
                <span className="calendar-day-header">Jue</span>
                <span className="calendar-day-header">Vie</span>
                <span className="calendar-day-header">Sáb</span>
                <span className="calendar-day-header">Dom</span>

                {/* Dynamic dynamic padding spacer cell based on weekday of day index 1 */}
                {Array.from({
                  length: (() => {
                    const firstDate = new Date(calendarMonthData.year, calendarMonthData.monthIndex, 1);
                    let idx = firstDate.getDay() - 1;
                    return idx === -1 ? 6 : idx;
                  })()
                }).map((_, spacerIdx) => (
                  <div key={`spacer-${spacerIdx}`} className="calendar-cell inactive" style={{ opacity: 0.15 }}>
                    <span className="calendar-day-num"></span>
                  </div>
                ))}

                {calendarMonthData.days.map((d) => {
                  const isSelected = selectedCalendarDayNum === d.dayNum;
                  const isSimulated = selectedDaySimulated.toLowerCase() === d.dayName.toLowerCase();

                  return (
                    <div
                      key={d.dayNum}
                      className={`calendar-cell ${isSelected ? 'active-simulated' : ''}`}
                      style={{
                        borderWidth: isSelected ? '2px' : '1px',
                        borderColor: isSelected ? 'var(--accent)' : 'var(--border-color)',
                        backgroundColor: isSelected ? 'var(--accent-light)' : (d.hasPromo ? '#f8f9fa' : 'transparent'),
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                        padding: '4px',
                        minHeight: '52px'
                      }}
                      onClick={() => {
                        setSelectedCalendarDayNum(d.dayNum);
                        setSelectedDaySimulated(d.dayName);
                      }}
                    >
                      <span className="calendar-day-num" style={{ fontWeight: isSelected ? '700' : 'normal', fontSize: '0.8rem' }}>
                        {d.dayNum}
                      </span>

                      {/* Mini dots or logos for promos */}
                      <div className="calendar-dot-container" style={{ display: 'flex', gap: '2px', overflow: 'hidden', flexWrap: 'wrap', justifyContent: 'center' }}>
                        {d.promos.slice(0, 3).map((p, pIdx) => {
                          const miniBenImg = getBenefitImage(p.name);
                          return miniBenImg ? (
                            <img
                              key={pIdx}
                              src={miniBenImg}
                              alt={p.name}
                              style={{ width: '10px', height: '10px', objectFit: 'contain', borderRadius: '50%' }}
                            />
                          ) : (
                            <span key={pIdx} style={{ fontSize: '0.5rem', background: '#ccc', borderRadius: '2px', padding: '0 1px' }}>%</span>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Day info detail banner */}
              <div className="combo-banner" style={{ marginTop: '0.5rem' }}>
                <CalendarDays style={{ width: '22px', height: '22px', color: 'var(--accent)', flexShrink: 0 }} />
                <div>
                  <h4 style={{ fontSize: '0.9rem', fontWeight: 'bold', marginBottom: '0.2rem', textTransform: 'capitalize' }}>
                    Descuentos del {selectedDayInfo.dayName} {selectedDayInfo.dayNum} de {calendarMonthData.monthName.split(' ')[0]}
                  </h4>
                  {selectedDayInfo.promos.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', marginTop: '0.35rem' }}>
                      {selectedDayInfo.promos.map((p, idx) => (
                        <div key={idx} style={{ fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span style={{ fontWeight: '700', color: 'var(--accent)' }}>{p.value}% OFF</span>
                          <span>en {p.supermercado} ({p.name})</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      No se encontraron promociones programadas para este día de la semana.
                    </p>
                  )}
                </div>
              </div>

              <div style={{ marginTop: '1.5rem', display: 'flex', justifyContent: 'flex-end' }}>
                <button
                  className="btn"
                  onClick={() => setActiveTab('cart')}
                  style={{ backgroundColor: 'var(--accent)', color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.6rem 1.2rem', borderRadius: '4px' }}
                >
                  Ir al Changuito <ChevronRight style={{ width: '16px', height: '16px' }} />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: SHOPPING CART & OPTIMIZER */}
        {activeTab === 'cart' && (
          <div className="step-container">
            <h2 className="step-title" style={{ fontFamily: 'var(--font-serif)' }}>¿Qué necesitás comprar?</h2>

            {/* Quick add / input */}
            <form onSubmit={handleAddCustomItem}>
              <div className="cart-input-wrapper">
                <ShoppingBag className="cart-input-icon" />
                <input
                  type="text"
                  className="cart-input"
                  placeholder="Agregar leche, fideos, carne..."
                  value={customItemText}
                  onChange={(e) => setCustomItemText(e.target.value)}
                />
                <button
                  type="submit"
                  style={{ position: 'absolute', right: '0.5rem', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--accent)', cursor: 'pointer', padding: '0.5rem' }}
                >
                  <Plus style={{ width: '20px', height: '20px' }} />
                </button>
              </div>
            </form>

            {/* Quick Add Pills */}
            <div className="quick-add-pills">
              {PRODUCT_CATALOG.filter(p => !cart.some(c => c.name === p.name)).slice(0, 4).map((p, idx) => (
                <div key={idx} className="pill" onClick={() => handleAddItem(p)}>
                  + {p.name}
                </div>
              ))}
            </div>

            {/* Shopping List */}
            {cart.length > 0 ? (
              <div className="shopping-list">
                {cart.map((item, idx) => {
                  const catalogItem = PRODUCT_CATALOG.find(p => p.name === item.name);
                  const lowestPrice = Math.min(...Object.values(item.basePrices));
                  const currentStore = (selectedBenefits.length > 0 && selectedBenefits[0].entries && selectedBenefits[0].entries[0]?.supermercado)
                    || results?.bestSingleStore
                    || 'Carrefour';
                  const itemPrice = item.basePrices[currentStore] || lowestPrice;
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
                            {item.selectedBrand || 'Genérico'} • ${itemPrice.toLocaleString('es-AR')} c/u
                          </span>
                        </div>
                      </div>

                      {/* Brand selector setting button + quantity controls */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                        <div style={{ textAlign: 'right', minWidth: '70px', marginRight: '0.25rem' }}>
                          <span style={{ fontSize: '0.9rem', fontWeight: '700', color: 'var(--text-primary)' }}>
                            ${itemSubtotal.toLocaleString('es-AR')}
                          </span>
                        </div>

                        {catalogItem && catalogItem.variants && (
                          <button
                            onClick={() => setActiveModalItemIndex(idx)}
                            style={{
                              background: 'var(--bg-secondary)',
                              border: '1px solid var(--border-color)',
                              fontSize: '0.7rem',
                              fontWeight: '600',
                              padding: '0.35rem 0.65rem',
                              borderRadius: '20px',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '4px',
                              color: 'var(--text-secondary)'
                            }}
                          >
                            <Maximize2 style={{ width: '11px', height: '11px' }} /> Marca
                          </button>
                        )}

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

                {/* Grand Total Row at the bottom of the list */}
                {(() => {
                  const currentStore = (selectedBenefits.length > 0 && selectedBenefits[0].entries && selectedBenefits[0].entries[0]?.supermercado)
                    || results?.bestSingleStore
                    || 'Carrefour';
                  return (
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '1rem',
                      borderTop: '2px solid var(--border-color)',
                      marginTop: '1rem',
                      backgroundColor: 'var(--accent-light)',
                      border: '1px solid var(--accent)',
                      borderRadius: '8px'
                    }}>
                      <div>
                        <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'block', fontWeight: '500' }}>
                          Total estimado en <strong>{currentStore}</strong>
                        </span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
                          {cart.reduce((s, i) => s + i.quantity, 0)} unidades
                        </span>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <span style={{ fontSize: '1.4rem', fontWeight: '800', color: 'var(--accent)', fontFamily: 'var(--font-serif)' }}>
                          ${(results?.baseTotals[currentStore] || 0).toLocaleString('es-AR')}
                        </span>
                      </div>
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

                {/* Real Total Cards */}
                <div className="financial-overview">
                  <div className="financial-card">
                    <span className="financial-label">Total en {results.bestSingleStore}</span>
                    <span className="financial-value">${results.baseTotals[results.bestSingleStore]?.toLocaleString('es-AR')}</span>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-tertiary)' }}>{cart.reduce((s, i) => s + i.quantity, 0)} productos</span>
                  </div>
                  <div className="financial-card" style={{ borderColor: 'var(--accent)' }}>
                    <span className="financial-label">Pagás con descuento</span>
                    <span className="financial-value financial-accent">${results.discountedTotals[results.bestSingleStore]?.toLocaleString('es-AR')}</span>
                    {results.savingsAmount[results.bestSingleStore] > 0 && (
                      <span style={{ fontSize: '0.7rem', color: '#16a34a', fontWeight: '600' }}>Ahorrás ${results.savingsAmount[results.bestSingleStore]?.toLocaleString('es-AR')}</span>
                    )}
                  </div>
                </div>

                {/* Single Store Rank Card - Information Cartography */}
                <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem', fontFamily: 'var(--font-serif)' }}>Comparación de Canasta</h3>
                <div className="store-comparison-list">
                  {supermarkets.map(store => {
                    const isBest = store === results.bestSingleStore;

                    // Determine supermarket logo path
                    let logoSrc = null;
                    const storeLower = store.toLowerCase();
                    if (storeLower === "coto") {
                      logoSrc = "/visuales/spk_assets/coto.webp";
                    } else if (storeLower === "carrefour") {
                      logoSrc = "/visuales/spk_assets/carrefour.svg";
                    } else if (storeLower === "dia") {
                      logoSrc = "/visuales/spk_assets/dia.svg";
                    } else if (storeLower === "jumbo") {
                      logoSrc = "/visuales/spk_assets/jumbo.svg";
                    } else if (storeLower === "disco") {
                      logoSrc = "/visuales/spk_assets/disco.svg";
                    } else if (storeLower === "vea") {
                      logoSrc = "/visuales/spk_assets/vea.webp";
                    }

                    return (
                      <div
                        key={store}
                        className={`store-comparison-row ${isBest ? 'best' : ''}`}
                        style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.6rem 0', borderBottom: '1px solid var(--border-color)' }}
                      >
                        <span style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                          {logoSrc ? (
                            <img
                              src={logoSrc}
                              alt={store}
                              style={{ width: '28px', height: '28px', objectFit: 'contain' }}
                            />
                          ) : (
                            <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: isBest ? 'var(--accent)' : 'var(--text-tertiary)' }} />
                          )}
                          <span style={{ fontWeight: isBest ? '700' : 'normal' }}>
                            {store} {isBest && '(Mejor Opción)'}
                          </span>
                        </span>
                        <span>
                          ${results.discountedTotals[store]?.toLocaleString('es-AR')}
                          {results.savingsAmount[store] > 0 && (
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginLeft: '0.5rem' }}>
                              (-${results.savingsAmount[store]})
                            </span>
                          )}
                        </span>
                      </div>
                    );
                  })}
                </div>

                {/* CompraIQ Smart Suggestions Banners */}
                <h3 style={{ fontSize: '1.15rem', marginTop: '1rem', marginBottom: '0.5rem', fontFamily: 'var(--font-serif)' }}>Recomendación Inteligente</h3>

                {selectedBenefits.length === 0 ? (
                  <div className="combo-banner" style={{ borderStyle: 'dashed', backgroundColor: 'transparent' }}>
                    <Info style={{ width: '18px', height: '18px', color: 'var(--text-tertiary)' }} />
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      No tenés beneficios activados. Agregá tus tarjetas en Onboarding para calcular descuentos del día.
                    </p>
                  </div>
                ) : (
                  <div className="combo-banner">
                    <Sparkles style={{ width: '18px', height: '18px', color: 'var(--accent)' }} />
                    <div>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-primary)', fontWeight: 'bold' }}>
                        Compra optimizada para el {selectedDaySimulated}:
                      </p>
                      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                        Si compras hoy en <strong>{results.bestSingleStore}</strong> con tus beneficios guardados, ahorrás un total de <strong>${results.savingsAmount[results.bestSingleStore]}</strong>.
                      </p>

                      {/* Dynamic tips based on selectedDaySimulated and basket contents */}
                      {selectedDaySimulated.toLowerCase() === 'miércoles' && (
                        <p style={{ fontSize: '0.8rem', color: 'var(--accent)', marginTop: '0.4rem', fontWeight: '500' }}>
                          💡 Tip: Si hoy es Miércoles y tenés Cuenta DNI, recordá que tenés 20% de reintegro en Dia y Carrefour.
                        </p>
                      )}
                      {selectedDaySimulated.toLowerCase() === 'viernes' && (
                        <p style={{ fontSize: '0.8rem', color: 'var(--accent)', marginTop: '0.4rem', fontWeight: '500' }}>
                          💡 Tip: Si comprás Carnes en Coto el viernes con tu tarjeta Galicia, ahorrás 15% extra.
                        </p>
                      )}
                      {selectedDaySimulated.toLowerCase() === 'lunes' && (
                        <p style={{ fontSize: '0.8rem', color: 'var(--accent)', marginTop: '0.4rem', fontWeight: '500' }}>
                          💡 Tip: Recordá que los Lunes tenés 10% en Carrefour con Visa y descuentos exclusivos de Coto Club.
                        </p>
                      )}
                    </div>
                  </div>
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
          className={`footer-nav-btn ${activeTab === 'calendar' ? 'active' : ''}`}
          onClick={() => setActiveTab('calendar')}
        >
          <Calendar style={{ width: '20px', height: '20px' }} />
          <span>Calendario</span>
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
                          ${b.price?.toLocaleString('es-AR')}
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
                          ${s.cheapestBrand.price.toLocaleString('es-AR')}
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
