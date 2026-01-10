/**
 * EOS Platform - Internationalization (i18n) Configuration
 */
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Translation resources
const resources = {
  en: {
    translation: {
      // Navigation
      nav: {
        dashboard: 'Dashboard',
        projects: 'Projects',
        campaigns: 'Campaigns',
        mediaPlans: 'Media Plans',
        reports: 'Reports',
        admin: 'Administration',
        users: 'Users',
        clients: 'Clients',
        labels: 'Labels',
        workflows: 'Workflows',
      },
      // Common
      common: {
        save: 'Save',
        cancel: 'Cancel',
        delete: 'Delete',
        edit: 'Edit',
        create: 'Create',
        search: 'Search',
        filter: 'Filter',
        loading: 'Loading...',
        noResults: 'No results found',
        actions: 'Actions',
        status: 'Status',
        name: 'Name',
        code: 'Code',
        description: 'Description',
        startDate: 'Start Date',
        endDate: 'End Date',
        budget: 'Budget',
        currency: 'Currency',
        active: 'Active',
        inactive: 'Inactive',
        required: 'Required',
        optional: 'Optional',
      },
      // Status
      status: {
        draft: 'Draft',
        active: 'Active',
        paused: 'Paused',
        completed: 'Completed',
        cancelled: 'Cancelled',
        pendingApproval: 'Pending Approval',
        approved: 'Approved',
        rejected: 'Rejected',
      },
      // Auth
      auth: {
        signIn: 'Sign In',
        signOut: 'Sign Out',
        email: 'Email',
        password: 'Password',
        rememberMe: 'Remember me',
        forgotPassword: 'Forgot password?',
        invalidCredentials: 'Invalid email or password',
      },
      // Dashboard
      dashboard: {
        welcome: 'Welcome back',
        overview: 'Overview',
        activeCampaigns: 'Active Campaigns',
        totalBudget: 'Total Budget',
        budgetUtilization: 'Budget Utilization',
        pendingApprovals: 'Pending Approvals',
        recentActivity: 'Recent Activity',
        quickActions: 'Quick Actions',
      },
      // Projects
      projects: {
        title: 'Projects',
        subtitle: 'Manage your advertising projects',
        newProject: 'New Project',
        advertiser: 'Advertiser',
        campaigns: 'Campaigns',
      },
      // Campaigns
      campaigns: {
        title: 'Campaigns',
        subtitle: 'Manage your advertising campaigns',
        newCampaign: 'New Campaign',
        campaignType: 'Campaign Type',
        objective: 'Objective',
        targetAudience: 'Target Audience',
        spent: 'Spent',
        types: {
          brand: 'Brand',
          performance: 'Performance',
          awareness: 'Awareness',
          consideration: 'Consideration',
          conversion: 'Conversion',
        },
      },
      // Media Plans
      mediaPlans: {
        title: 'Media Plans',
        subtitle: 'Manage your media planning documents',
        newMediaPlan: 'New Media Plan',
        version: 'Version',
        subcampaigns: 'Subcampaigns',
        approve: 'Approve',
        reject: 'Reject',
        createVersion: 'Create Version',
      },
      // Subcampaigns
      subcampaigns: {
        title: 'Subcampaigns',
        channel: 'Channel',
        platform: 'Platform',
        adFormat: 'Ad Format',
        buyType: 'Buy Type',
        impressions: 'Impressions',
        clicks: 'Clicks',
        cpm: 'CPM',
        cpc: 'CPC',
        channels: {
          programmatic: 'Programmatic',
          social: 'Social',
          search: 'Search',
          display: 'Display',
          video: 'Video',
          native: 'Native',
          audio: 'Audio',
          ooh: 'OOH',
          tv: 'TV',
          print: 'Print',
          other: 'Other',
        },
      },
      // Reports
      reports: {
        title: 'Reports',
        subtitle: 'Analytics and insights for your campaigns',
        export: 'Export',
        dateRange: 'Date Range',
        overview: 'Overview',
        performance: 'Performance',
      },
      // Admin
      admin: {
        users: {
          title: 'Users',
          subtitle: 'Manage user accounts and permissions',
          newUser: 'Add User',
          role: 'Role',
          lastLogin: 'Last Login',
        },
        clients: {
          title: 'Clients',
          subtitle: 'Manage client accounts',
          newClient: 'Add Client',
          costCenter: 'Cost Center',
          contactName: 'Contact Name',
        },
        labels: {
          title: 'Labels',
          subtitle: 'Manage taxonomy and classification labels',
          newLabel: 'Add Label',
          maxLabels: 'Maximum of 20 labels allowed per tenant',
          labelType: 'Label Type',
          values: 'Values',
        },
        workflows: {
          title: 'Workflows',
          subtitle: 'Manage approval workflows and state machines',
          states: 'States',
          transitions: 'Transitions',
          pendingApprovals: 'Pending Approvals',
        },
      },
      // Portal
      portal: {
        welcome: 'Welcome to the Client Portal',
        dashboard: 'Dashboard',
        campaigns: 'My Campaigns',
        approvals: 'Approvals',
        noApprovals: 'No pending approvals',
        allReviewed: 'All media plans have been reviewed',
      },
      // Errors
      errors: {
        general: 'An error occurred. Please try again.',
        notFound: 'Not found',
        unauthorized: 'Unauthorized access',
        sessionExpired: 'Session expired. Please login again.',
      },
    },
  },
  es: {
    translation: {
      // Navigation
      nav: {
        dashboard: 'Panel',
        projects: 'Proyectos',
        campaigns: 'Campañas',
        mediaPlans: 'Planes de Medios',
        reports: 'Informes',
        admin: 'Administración',
        users: 'Usuarios',
        clients: 'Clientes',
        labels: 'Etiquetas',
        workflows: 'Flujos de Trabajo',
      },
      // Common
      common: {
        save: 'Guardar',
        cancel: 'Cancelar',
        delete: 'Eliminar',
        edit: 'Editar',
        create: 'Crear',
        search: 'Buscar',
        filter: 'Filtrar',
        loading: 'Cargando...',
        noResults: 'No se encontraron resultados',
        actions: 'Acciones',
        status: 'Estado',
        name: 'Nombre',
        code: 'Código',
        description: 'Descripción',
        startDate: 'Fecha de Inicio',
        endDate: 'Fecha de Fin',
        budget: 'Presupuesto',
        currency: 'Moneda',
        active: 'Activo',
        inactive: 'Inactivo',
        required: 'Requerido',
        optional: 'Opcional',
      },
      // Status
      status: {
        draft: 'Borrador',
        active: 'Activo',
        paused: 'Pausado',
        completed: 'Completado',
        cancelled: 'Cancelado',
        pendingApproval: 'Pendiente de Aprobación',
        approved: 'Aprobado',
        rejected: 'Rechazado',
      },
      // Auth
      auth: {
        signIn: 'Iniciar Sesión',
        signOut: 'Cerrar Sesión',
        email: 'Correo Electrónico',
        password: 'Contraseña',
        rememberMe: 'Recordarme',
        forgotPassword: '¿Olvidaste tu contraseña?',
        invalidCredentials: 'Correo o contraseña inválidos',
      },
      // Dashboard
      dashboard: {
        welcome: 'Bienvenido de nuevo',
        overview: 'Resumen',
        activeCampaigns: 'Campañas Activas',
        totalBudget: 'Presupuesto Total',
        budgetUtilization: 'Utilización del Presupuesto',
        pendingApprovals: 'Aprobaciones Pendientes',
        recentActivity: 'Actividad Reciente',
        quickActions: 'Acciones Rápidas',
      },
      // Projects
      projects: {
        title: 'Proyectos',
        subtitle: 'Gestiona tus proyectos publicitarios',
        newProject: 'Nuevo Proyecto',
        advertiser: 'Anunciante',
        campaigns: 'Campañas',
      },
      // Campaigns
      campaigns: {
        title: 'Campañas',
        subtitle: 'Gestiona tus campañas publicitarias',
        newCampaign: 'Nueva Campaña',
        campaignType: 'Tipo de Campaña',
        objective: 'Objetivo',
        targetAudience: 'Audiencia Objetivo',
        spent: 'Gastado',
        types: {
          brand: 'Marca',
          performance: 'Rendimiento',
          awareness: 'Conocimiento',
          consideration: 'Consideración',
          conversion: 'Conversión',
        },
      },
      // Media Plans
      mediaPlans: {
        title: 'Planes de Medios',
        subtitle: 'Gestiona tus documentos de planificación',
        newMediaPlan: 'Nuevo Plan de Medios',
        version: 'Versión',
        subcampaigns: 'Subcampañas',
        approve: 'Aprobar',
        reject: 'Rechazar',
        createVersion: 'Crear Versión',
      },
      // Subcampaigns
      subcampaigns: {
        title: 'Subcampañas',
        channel: 'Canal',
        platform: 'Plataforma',
        adFormat: 'Formato de Anuncio',
        buyType: 'Tipo de Compra',
        impressions: 'Impresiones',
        clicks: 'Clics',
        cpm: 'CPM',
        cpc: 'CPC',
        channels: {
          programmatic: 'Programática',
          social: 'Social',
          search: 'Búsqueda',
          display: 'Display',
          video: 'Video',
          native: 'Nativo',
          audio: 'Audio',
          ooh: 'Exterior',
          tv: 'TV',
          print: 'Impreso',
          other: 'Otro',
        },
      },
      // Reports
      reports: {
        title: 'Informes',
        subtitle: 'Analíticas e insights de tus campañas',
        export: 'Exportar',
        dateRange: 'Rango de Fechas',
        overview: 'Resumen',
        performance: 'Rendimiento',
      },
      // Admin
      admin: {
        users: {
          title: 'Usuarios',
          subtitle: 'Gestiona cuentas y permisos de usuarios',
          newUser: 'Añadir Usuario',
          role: 'Rol',
          lastLogin: 'Último Acceso',
        },
        clients: {
          title: 'Clientes',
          subtitle: 'Gestiona cuentas de clientes',
          newClient: 'Añadir Cliente',
          costCenter: 'Centro de Costes',
          contactName: 'Nombre de Contacto',
        },
        labels: {
          title: 'Etiquetas',
          subtitle: 'Gestiona taxonomía y etiquetas de clasificación',
          newLabel: 'Añadir Etiqueta',
          maxLabels: 'Máximo de 20 etiquetas permitidas por tenant',
          labelType: 'Tipo de Etiqueta',
          values: 'Valores',
        },
        workflows: {
          title: 'Flujos de Trabajo',
          subtitle: 'Gestiona flujos de aprobación y máquinas de estado',
          states: 'Estados',
          transitions: 'Transiciones',
          pendingApprovals: 'Aprobaciones Pendientes',
        },
      },
      // Portal
      portal: {
        welcome: 'Bienvenido al Portal de Cliente',
        dashboard: 'Panel',
        campaigns: 'Mis Campañas',
        approvals: 'Aprobaciones',
        noApprovals: 'Sin aprobaciones pendientes',
        allReviewed: 'Todos los planes de medios han sido revisados',
      },
      // Errors
      errors: {
        general: 'Ha ocurrido un error. Por favor, inténtalo de nuevo.',
        notFound: 'No encontrado',
        unauthorized: 'Acceso no autorizado',
        sessionExpired: 'Sesión expirada. Por favor, inicia sesión de nuevo.',
      },
    },
  },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'es',
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
  });

export default i18n;
