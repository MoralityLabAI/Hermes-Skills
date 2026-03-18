import { TEMPO_MODERATO } from '../config/tempo.js'

export type SponsorProfile = {
  kind: 'public-testnet' | 'self-hosted'
  url: string
  enabled: boolean
}

export function defaultSponsorProfile(): SponsorProfile {
  return {
    kind: 'public-testnet',
    url: TEMPO_MODERATO.sponsorUrl ?? '',
    enabled: false,
  }
}

export function renderSponsorInstructions(profile = defaultSponsorProfile()): string {
  return [
    `kind=${profile.kind}`,
    `url=${profile.url}`,
    `enabled=${String(profile.enabled)}`,
    'Tempo docs describe dual signature domains and a fee payer envelope.',
    'Treat the public sponsor endpoint as a development/testnet convenience only.',
  ].join('\n')
}
