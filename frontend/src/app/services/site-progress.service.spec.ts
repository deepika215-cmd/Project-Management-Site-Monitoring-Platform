import { describe, it, expect } from 'vitest';
import { HttpClient } from '@angular/common/http';
import { SiteProgressService } from './site-progress.service';

describe('SiteProgressService', () => {
  it('returns an empty progress list initially', () => {
    const service = new SiteProgressService({} as HttpClient);
    expect(service.getProgressEntries()).toEqual([]);
  });
});
