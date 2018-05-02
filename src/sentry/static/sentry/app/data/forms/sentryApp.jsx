export default [
  {
    title: 'Details',
    fields: [
      {
        name: 'name',
        type: 'string',
        required: true,
        label: 'Name',
      },
      {
        name: 'homepage_url',
        type: 'string',
        required: false,
        label: 'Homepage',
        placeholder: 'e.g. https://example.com/',
        help: "An optional link to your application's homepage",
      },
      {
        name: 'privacy_url',
        type: 'string',
        label: 'Privacy Policy',
        placeholder: 'e.g. https://example.com/privacy',
        help: 'An optional link to your Privacy Policy',
      },
      {
        name: 'terms_url',
        type: 'string',
        label: 'Terms of Service',
        placeholder: 'e.g. https://example.com/terms',
        help: 'An optional link to your Terms of Service agreement',
      },
    ],
  },

  {
    title: 'Integration',
    fields: [
      {
        name: 'webhook_url',
        type: 'string',
        placeholder: 'e.g. https://example.com/sentry-apps',
        label: 'Webhook URL',
        help: "URL where you'll receive install, upgrade, and uninstall requests.",
        required: true,
      },
    ],
  },
];
