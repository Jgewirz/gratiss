# SkinStack - Influencer Skincare Affiliate Platform
## Logical File Structure

```
skinstack/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── package.json
├── tsconfig.json
├── README.md
│
├── src/
│   ├── main.ts                     # Application entry point
│   ├── app.module.ts               # Root module (NestJS)
│   │
│   ├── config/
│   │   ├── app.config.ts           # Application configuration
│   │   ├── database.config.ts      # Database configuration
│   │   ├── redis.config.ts         # Redis configuration
│   │   ├── aws.config.ts           # AWS services configuration
│   │   └── networks.config.ts      # Affiliate networks configuration
│   │
│   ├── database/
│   │   ├── migrations/
│   │   │   ├── 001_create_users_table.sql
│   │   │   ├── 002_create_influencers_table.sql
│   │   │   ├── 003_create_merchants_table.sql
│   │   │   ├── 004_create_networks_table.sql
│   │   │   ├── 005_create_programs_table.sql
│   │   │   ├── 006_create_products_table.sql
│   │   │   ├── 007_create_tracking_links_table.sql
│   │   │   ├── 008_create_clicks_table.sql
│   │   │   ├── 009_create_conversions_table.sql
│   │   │   ├── 010_create_attributions_table.sql
│   │   │   ├── 011_create_commissions_table.sql
│   │   │   ├── 012_create_payouts_table.sql
│   │   │   ├── 013_create_reversals_table.sql
│   │   │   ├── 014_create_campaigns_table.sql
│   │   │   ├── 015_create_consents_table.sql
│   │   │   └── 016_create_webhook_events_table.sql
│   │   ├── seeds/
│   │   │   └── initial_data.sql
│   │   └── connection.ts            # Database connection manager
│   │
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── auth.module.ts
│   │   │   ├── auth.controller.ts
│   │   │   ├── auth.service.ts
│   │   │   ├── jwt.strategy.ts
│   │   │   ├── oauth.strategy.ts
│   │   │   └── dto/
│   │   │       ├── login.dto.ts
│   │   │       └── register.dto.ts
│   │   │
│   │   ├── users/
│   │   │   ├── users.module.ts
│   │   │   ├── users.controller.ts
│   │   │   ├── users.service.ts
│   │   │   ├── entities/
│   │   │   │   └── user.entity.ts
│   │   │   └── dto/
│   │   │       ├── create-user.dto.ts
│   │   │       └── update-user.dto.ts
│   │   │
│   │   ├── influencers/
│   │   │   ├── influencers.module.ts
│   │   │   ├── influencers.controller.ts
│   │   │   ├── influencers.service.ts
│   │   │   ├── entities/
│   │   │   │   └── influencer.entity.ts
│   │   │   └── dto/
│   │   │       ├── create-influencer.dto.ts
│   │   │       └── update-influencer.dto.ts
│   │   │
│   │   ├── merchants/
│   │   │   ├── merchants.module.ts
│   │   │   ├── merchants.controller.ts
│   │   │   ├── merchants.service.ts
│   │   │   ├── entities/
│   │   │   │   └── merchant.entity.ts
│   │   │   └── dto/
│   │   │       └── create-merchant.dto.ts
│   │   │
│   │   ├── tracking/
│   │   │   ├── tracking.module.ts
│   │   │   ├── links/
│   │   │   │   ├── links.controller.ts
│   │   │   │   ├── links.service.ts
│   │   │   │   ├── link-generator.service.ts
│   │   │   │   └── entities/
│   │   │   │       └── tracking-link.entity.ts
│   │   │   ├── clicks/
│   │   │   │   ├── clicks.controller.ts
│   │   │   │   ├── clicks.service.ts
│   │   │   │   ├── click-processor.service.ts
│   │   │   │   └── entities/
│   │   │   │       └── click.entity.ts
│   │   │   └── dto/
│   │   │       ├── create-link.dto.ts
│   │   │       └── track-click.dto.ts
│   │   │
│   │   ├── attribution/
│   │   │   ├── attribution.module.ts
│   │   │   ├── attribution.service.ts
│   │   │   ├── models/
│   │   │   │   ├── last-click.model.ts
│   │   │   │   ├── first-click.model.ts
│   │   │   │   └── multi-touch.model.ts
│   │   │   └── entities/
│   │   │       └── attribution.entity.ts
│   │   │
│   │   ├── conversions/
│   │   │   ├── conversions.module.ts
│   │   │   ├── conversions.controller.ts
│   │   │   ├── conversions.service.ts
│   │   │   ├── conversion-processor.service.ts
│   │   │   └── entities/
│   │   │       └── conversion.entity.ts
│   │   │
│   │   ├── commissions/
│   │   │   ├── commissions.module.ts
│   │   │   ├── commissions.service.ts
│   │   │   ├── commission-calculator.service.ts
│   │   │   ├── commission-rules.service.ts
│   │   │   └── entities/
│   │   │       ├── commission.entity.ts
│   │   │       └── reversal.entity.ts
│   │   │
│   │   ├── payouts/
│   │   │   ├── payouts.module.ts
│   │   │   ├── payouts.controller.ts
│   │   │   ├── payouts.service.ts
│   │   │   ├── payout-processor.service.ts
│   │   │   ├── providers/
│   │   │   │   ├── stripe.provider.ts
│   │   │   │   ├── paypal.provider.ts
│   │   │   │   └── ach.provider.ts
│   │   │   └── entities/
│   │   │       └── payout.entity.ts
│   │   │
│   │   ├── webhooks/
│   │   │   ├── webhooks.module.ts
│   │   │   ├── webhooks.controller.ts
│   │   │   ├── webhook-processor.service.ts
│   │   │   ├── webhook-verifier.service.ts
│   │   │   └── entities/
│   │   │       └── webhook-event.entity.ts
│   │   │
│   │   ├── integrations/
│   │   │   ├── integrations.module.ts
│   │   │   ├── base.integration.ts
│   │   │   ├── shopify/
│   │   │   │   ├── shopify.service.ts
│   │   │   │   ├── shopify-webhook.handler.ts
│   │   │   │   └── shopify.types.ts
│   │   │   ├── refersion/
│   │   │   │   ├── refersion.service.ts
│   │   │   │   ├── refersion-webhook.handler.ts
│   │   │   │   └── refersion.types.ts
│   │   │   ├── impact/
│   │   │   │   ├── impact.service.ts
│   │   │   │   ├── impact-postback.handler.ts
│   │   │   │   └── impact.types.ts
│   │   │   ├── amazon/
│   │   │   │   ├── amazon.service.ts
│   │   │   │   ├── amazon-link.builder.ts
│   │   │   │   └── amazon.types.ts
│   │   │   └── levanta/
│   │   │       ├── levanta.service.ts
│   │   │       └── levanta.types.ts
│   │   │
│   │   ├── products/
│   │   │   ├── products.module.ts
│   │   │   ├── products.controller.ts
│   │   │   ├── products.service.ts
│   │   │   ├── product-importer.service.ts
│   │   │   └── entities/
│   │   │       └── product.entity.ts
│   │   │
│   │   ├── programs/
│   │   │   ├── programs.module.ts
│   │   │   ├── programs.controller.ts
│   │   │   ├── programs.service.ts
│   │   │   └── entities/
│   │   │       └── program.entity.ts
│   │   │
│   │   ├── campaigns/
│   │   │   ├── campaigns.module.ts
│   │   │   ├── campaigns.controller.ts
│   │   │   ├── campaigns.service.ts
│   │   │   └── entities/
│   │   │       └── campaign.entity.ts
│   │   │
│   │   ├── analytics/
│   │   │   ├── analytics.module.ts
│   │   │   ├── analytics.controller.ts
│   │   │   ├── analytics.service.ts
│   │   │   ├── metrics/
│   │   │   │   ├── clicks.metrics.ts
│   │   │   │   ├── conversion.metrics.ts
│   │   │   │   ├── revenue.metrics.ts
│   │   │   │   └── influencer.metrics.ts
│   │   │   └── reports/
│   │   │       ├── performance.report.ts
│   │   │       └── payout.report.ts
│   │   │
│   │   ├── fraud/
│   │   │   ├── fraud.module.ts
│   │   │   ├── fraud-detection.service.ts
│   │   │   ├── rules/
│   │   │   │   ├── velocity.rule.ts
│   │   │   │   ├── fingerprint.rule.ts
│   │   │   │   ├── proxy-vpn.rule.ts
│   │   │   │   └── bot-detection.rule.ts
│   │   │   └── entities/
│   │   │       └── fraud-flag.entity.ts
│   │   │
│   │   └── compliance/
│   │       ├── compliance.module.ts
│   │       ├── privacy/
│   │       │   ├── privacy.controller.ts
│   │       │   ├── privacy.service.ts
│   │       │   ├── consent.service.ts
│   │       │   └── entities/
│   │       │       └── consent.entity.ts
│   │       └── tax/
│   │           ├── tax.service.ts
│   │           └── tax-form.service.ts
│   │
│   ├── common/
│   │   ├── decorators/
│   │   │   ├── api-key.decorator.ts
│   │   │   └── rate-limit.decorator.ts
│   │   ├── filters/
│   │   │   ├── http-exception.filter.ts
│   │   │   └── validation.filter.ts
│   │   ├── guards/
│   │   │   ├── jwt-auth.guard.ts
│   │   │   ├── api-key.guard.ts
│   │   │   └── roles.guard.ts
│   │   ├── interceptors/
│   │   │   ├── logging.interceptor.ts
│   │   │   └── transform.interceptor.ts
│   │   ├── pipes/
│   │   │   └── validation.pipe.ts
│   │   └── utils/
│   │       ├── hash.util.ts
│   │       ├── slug.util.ts
│   │       └── currency.util.ts
│   │
│   ├── queue/
│   │   ├── queue.module.ts
│   │   ├── processors/
│   │   │   ├── click.processor.ts
│   │   │   ├── conversion.processor.ts
│   │   │   ├── payout.processor.ts
│   │   │   └── webhook.processor.ts
│   │   └── producers/
│   │       └── event.producer.ts
│   │
│   └── edge/
│       ├── redirect/
│       │   ├── lambda.ts           # CloudFront Lambda@Edge
│       │   └── handler.ts
│       └── pixel/
│           └── tracker.ts
│
├── test/
│   ├── unit/
│   │   ├── services/
│   │   ├── controllers/
│   │   └── utils/
│   ├── integration/
│   │   ├── webhooks/
│   │   ├── api/
│   │   └── database/
│   └── e2e/
│       ├── auth.e2e-spec.ts
│       ├── tracking.e2e-spec.ts
│       └── payout.e2e-spec.ts
│
├── scripts/
│   ├── migrate.ts
│   ├── seed.ts
│   ├── reconcile.ts
│   └── payout-run.ts
│
├── docs/
│   ├── api/
│   │   ├── openapi.yaml
│   │   └── postman-collection.json
│   ├── integrations/
│   │   ├── shopify-setup.md
│   │   ├── impact-setup.md
│   │   └── amazon-setup.md
│   └── architecture/
│       ├── system-design.md
│       ├── database-schema.md
│       └── attribution-flow.md
│
├── infrastructure/
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── modules/
│   │       ├── ecs/
│   │       ├── rds/
│   │       └── cloudfront/
│   ├── kubernetes/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── ingress.yaml
│   └── docker/
│       ├── Dockerfile
│       └── nginx.conf
│
└── monitoring/
    ├── grafana/
    │   └── dashboards/
    ├── prometheus/
    │   └── alerts.yaml
    └── logging/
        └── logstash.conf
```

## Key Design Decisions

### 1. Module Organization
- **Feature-based modules**: Each major feature (tracking, attribution, commissions) has its own module
- **Shared common utilities**: Reusable components in `common/` directory
- **Integration abstraction**: All external networks under `integrations/` with common interface

### 2. Database Strategy
- **Migrations**: Numbered SQL files for version control
- **Entities**: TypeORM/Prisma entities co-located with modules
- **JSONB fields**: For flexible metadata storage

### 3. Service Architecture
- **Service layer**: Business logic separated from controllers
- **Queue processors**: Async operations via SQS/Kafka
- **Edge functions**: CloudFront Lambda@Edge for low-latency redirects

### 4. Security & Compliance
- **Authentication**: OAuth2/JWT with multiple strategies
- **Privacy module**: GDPR/CCPA compliance built-in
- **Fraud detection**: Rule-based system with ML-ready schema

### 5. Integration Pattern
- **Base integration class**: Common interface for all networks
- **Webhook handlers**: Network-specific webhook processors
- **Type safety**: TypeScript interfaces for each network's data

## Development Workflow

### Week 1-2: Core Infrastructure
- Database schemas and migrations
- Authentication and user management
- Basic tracking link generation
- Click tracking with Redis caching
- Shopify/Refersion webhook integration

### Week 3-4: Influencer Features
- Link management endpoints
- Statistics and analytics
- Basic fraud detection
- Merchant onboarding

### Week 5-6: Financial Operations
- Commission calculation engine
- Impact.com integration
- Return/reversal handling
- Payout processing via Stripe

### Week 7-8: Optimization & Scale
- Amazon Associates integration
- Advanced analytics
- Performance optimization
- API documentation

## Environment Variables (.env)

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/skinstack
REDIS_URL=redis://localhost:6379

# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
S3_BUCKET=skinstack-assets

# Auth
JWT_SECRET=xxx
OAUTH_CLIENT_ID=xxx
OAUTH_CLIENT_SECRET=xxx

# Payment Providers
STRIPE_SECRET_KEY=xxx
PAYPAL_CLIENT_ID=xxx
PAYPAL_SECRET=xxx

# Affiliate Networks
SHOPIFY_WEBHOOK_SECRET=xxx
REFERSION_API_KEY=xxx
IMPACT_ACCOUNT_SID=xxx
IMPACT_AUTH_TOKEN=xxx
AMAZON_ASSOCIATE_TAG=xxx
LEVANTA_API_KEY=xxx

# Monitoring
SENTRY_DSN=xxx
```

## Testing Strategy

1. **Unit Tests**: Service methods, utilities, calculators
2. **Integration Tests**: API endpoints, webhook handlers, database operations
3. **E2E Tests**: Complete user journeys (create link → click → conversion → payout)
4. **Performance Tests**: Load testing for click tracking, attribution processing

## Deployment

1. **Development**: Local Docker environment
2. **Staging**: AWS ECS with RDS
3. **Production**: Multi-AZ ECS, Aurora PostgreSQL, CloudFront distribution
4. **CI/CD**: GitHub Actions → AWS CodePipeline

## Monitoring & Observability

- **Metrics**: Prometheus + Grafana dashboards
- **Logging**: CloudWatch/ELK stack
- **Tracing**: OpenTelemetry → Jaeger
- **Alerts**: PagerDuty integration for critical issues