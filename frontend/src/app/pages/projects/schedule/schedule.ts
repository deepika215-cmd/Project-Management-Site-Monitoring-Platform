import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';


interface Activity {

  id: number;

  name: string;

  description: string;

  startDate: string;

  endDate: string;

  duration: number;

  dependency: string;

  status: string;

}


@Component({

  selector: 'app-schedule',

  standalone: true,

  imports: [

    CommonModule,

    FormsModule,

    RouterLink

  ],

  templateUrl: './schedule.html',

  styleUrl: './schedule.css'

})


export class Schedule {


  selectedProject = 'BT-001';


  showModal = false;


  editingActivity = false;


  currentActivity: Activity = {

    id: 0,

    name: '',

    description: '',

    startDate: '',

    endDate: '',

    duration: 0,

    dependency: '',

    status: 'Not Started'

  };


  activities: Activity[] = [

    {

      id: 1,

      name: 'Site Preparation',

      description:
        'Clear and prepare the construction site.',

      startDate: '2026-01-15',

      endDate: '2026-02-15',

      duration: 31,

      dependency: '',

      status: 'Completed'

    },


    {

      id: 2,

      name: 'Foundation Work',

      description:
        'Construct foundation and underground structures.',

      startDate: '2026-02-16',

      endDate: '2026-03-30',

      duration: 42,

      dependency: 'Site Preparation',

      status: 'Completed'

    },


    {

      id: 3,

      name: 'Structural Construction',

      description:
        'Construct the main structural framework.',

      startDate: '2026-04-01',

      endDate: '2026-08-30',

      duration: 151,

      dependency: 'Foundation Work',

      status: 'In Progress'

    },


    {

      id: 4,

      name: 'Electrical Installation',

      description:
        'Install electrical wiring and systems.',

      startDate: '2026-09-01',

      endDate: '2026-11-30',

      duration: 90,

      dependency: 'Structural Construction',

      status: 'Not Started'

    },


    {

      id: 5,

      name: 'Plumbing Installation',

      description:
        'Install plumbing and water supply systems.',

      startDate: '2026-09-01',

      endDate: '2026-11-30',

      duration: 90,

      dependency: 'Structural Construction',

      status: 'Not Started'

    },


    {

      id: 6,

      name: 'Interior Finishing',

      description:
        'Complete flooring, painting and interior works.',

      startDate: '2026-12-01',

      endDate: '2027-03-30',

      duration: 120,

      dependency: 'Electrical Installation',

      status: 'Not Started'

    },


    {

      id: 7,

      name: 'Final Inspection',

      description:
        'Conduct final inspection and quality checks.',

      startDate: '2027-04-01',

      endDate: '2027-05-15',

      duration: 44,

      dependency: 'Interior Finishing',

      status: 'Not Started'

    },


    {

      id: 8,

      name: 'Project Handover',

      description:
        'Complete documentation and handover to client.',

      startDate: '2027-05-16',

      endDate: '2027-06-30',

      duration: 45,

      dependency: 'Final Inspection',

      status: 'Not Started'

    }

  ];


  get completedPercentage(): number {


    if (

      this.activities.length === 0

    ) {

      return 0;

    }


    const completed =

      this.activities.filter(

        activity =>

          activity.status ===

          'Completed'

      ).length;


    return Math.round(

      (completed /

        this.activities.length) *

        100

    );

  }


  getStatusCount(
    status: string
  ): number {


    return this.activities.filter(

      activity =>

        activity.status === status

    ).length;

  }


  getDelayedCount(): number {


    return this.activities.filter(

      activity =>

        activity.status === 'Delayed'

    ).length;

  }


  getStatusClass(
    status: string
  ): string {


    switch (status) {


      case 'Not Started':

        return 'not-started';


      case 'In Progress':

        return 'in-progress';


      case 'Completed':

        return 'completed';


      case 'Delayed':

        return 'delayed';


      default:

        return '';

    }

  }


  openAddActivity(): void {


    this.editingActivity =

      false;


    this.currentActivity = {


      id: 0,

      name: '',

      description: '',

      startDate: '',

      endDate: '',

      duration: 0,

      dependency: '',

      status: 'Not Started'

    };


    this.showModal = true;

  }


  editActivity(
    activity: Activity
  ): void {


    this.editingActivity =

      true;


    this.currentActivity = {

      ...activity

    };


    this.showModal = true;

  }


  saveActivity(): void {


    this.calculateDuration();


    if (

      this.editingActivity

    ) {


      const index =

        this.activities.findIndex(

          activity =>

            activity.id ===

            this.currentActivity.id

        );


      if (index !== -1) {


        this.activities[index] =

          {

            ...this.currentActivity

          };

      }


      alert(

        'Activity updated successfully!'

      );


    } else {


      const newActivity: Activity = {


        ...this.currentActivity,


        id:

          this.getNextId()

      };


      this.activities.push(

        newActivity

      );


      alert(

        'Activity added successfully!'

      );

    }


    this.closeModal();

  }


  calculateDuration(): void {


    if (

      !this.currentActivity.startDate ||

      !this.currentActivity.endDate

    ) {

      this.currentActivity.duration = 0;

      return;

    }


    const start =

      new Date(

        this.currentActivity.startDate

      );


    const end =

      new Date(

        this.currentActivity.endDate

      );


    const difference =

      end.getTime() -

      start.getTime();


    this.currentActivity.duration =

      Math.ceil(

        difference /

        (1000 * 60 * 60 * 24)

      ) + 1;

  }


  deleteActivity(
    id: number
  ): void {


    const confirmed =

      confirm(

        'Are you sure you want to delete this activity?'

      );


    if (!confirmed) {

      return;

    }


    this.activities =

      this.activities.filter(

        activity =>

          activity.id !== id

      );


    alert(

      'Activity deleted successfully!'

    );

  }


  closeModal(): void {


    this.showModal =

      false;

  }


  private getNextId(): number {


    if (

      this.activities.length === 0

    ) {

      return 1;

    }


    return Math.max(

      ...this.activities.map(

        activity =>

          activity.id

      )

    ) + 1;

  }

}