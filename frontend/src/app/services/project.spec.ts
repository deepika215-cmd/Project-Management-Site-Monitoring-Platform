import { TestBed } from '@angular/core/testing';
import { ProjectService } from './project';
import { Api } from './api';

describe('ProjectService', () => {
  let service: ProjectService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ProjectService, { provide: Api, useValue: {} }]
    });
    service = TestBed.inject(ProjectService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should map backend projects to the existing UI model', () => {
    const mapped = service.toViewModel({
      id: 7,
      project_name: 'Test Project',
      description: 'Description',
      location: 'Chennai',
      start_date: '2026-01-01',
      end_date: '2026-07-01',
      budget: 100000,
      status: 'Planning',
      manager_id: 3
    });

    expect(mapped.id).toBe(7);
    expect(mapped.name).toBe('Test Project');
    expect(mapped.code).toBe('BT-007');
    expect(mapped.managerId).toBe(3);
  });
});
