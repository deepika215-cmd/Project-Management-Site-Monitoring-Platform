import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';


interface Milestone {

  id: number;

  name: string;

  description: string;

  plannedDate: string;

  actualDate: string;

  status: string;

}


@Component({

  selector: 'app-milestones',

  standalone: true,

  imports: [

    CommonModule,

    FormsModule,

    RouterLink

  ],

  templateUrl: './milestones.html',

  styleUrl: './milestones.css'

})


export class Milestones {


  selectedProject = 'BT-001';


  showModal = false;


  editingMilestone = false;


  currentMilestone: Milestone = {

    id: 0,

    name: '',

    description: '',

    plannedDate: '',

    actualDate: '',

    status: 'Pending'

  };


  milestones: Milestone[] = [


    {

      id: 1,

      name:
        'Foundation Completed',

      description:
        'Completion of foundation and underground structural work.',

      plannedDate:
        '2026-03-15',

      actualDate:
        '2026-03-12',

      status:
        'Completed'

    },


    {

      id: 2,

      name:
        'Structural Work Completed',

      description:
        'Completion of major structural construction activities.',

      plannedDate:
        '2026-07-30',

      actualDate:
        '',

      status:
        'In Progress'

    },


    {

      id: 3,

      name:
        'Electrical Work Completed',

      description:
        'Completion of electrical wiring and installations.',

      plannedDate:
        '2026-10-30',

      actualDate:
        '',

      status:
        'Pending'

    },


    {

      id: 4,

      name:
        'Plumbing Completed',

      description:
        'Completion of plumbing and water supply systems.',

      plannedDate:
        '2026-11-30',

      actualDate:
        '',

      status:
        'Pending'

    },


    {

      id: 5,

      name:
        'Finishing Completed',

      description:
        'Completion of painting, flooring and interior finishing.',

      plannedDate:
        '2027-03-30',

      actualDate:
        '',

      status:
        'Pending'

    },


    {

      id: 6,

      name:
        'Final Inspection Completed',

      description:
        'Final inspection and quality verification of the project.',

      plannedDate:
        '2027-05-30',

      actualDate:
        '',

      status:
        'Pending'

    },


    {

      id: 7,

      name:
        'Project Handover',

      description:
        'Official handover of completed project to the client.',

      plannedDate:
        '2027-06-30',

      actualDate:
        '',

      status:
        'Pending'

    }

  ];


  get completedPercentage(): number {


    if (this.milestones.length === 0) {

      return 0;

    }


    const completed =

      this.milestones.filter(

        milestone =>

          milestone.status === 'Completed'

      ).length;


    return Math.round(

      (completed /

        this.milestones.length) *

        100

    );

  }


  getStatusCount(
    status: string
  ): number {


    return this.milestones.filter(

      milestone =>

        milestone.status === status

    ).length;

  }


  getDelayedCount(): number {


    return this.milestones.filter(

      milestone =>

        this.isDelayed(milestone)

    ).length;

  }


  isDelayed(
    milestone: Milestone
  ): boolean {


    if (

      milestone.status ===

      'Completed'

    ) {

      return false;

    }


    if (

      milestone.status ===

      'Delayed'

    ) {

      return true;

    }


    if (

      !milestone.plannedDate

    ) {

      return false;

    }


    const today =

      new Date();


    const plannedDate =

      new Date(

        milestone.plannedDate

      );


    return (

      today >

      plannedDate

    );

  }


  getStatusClass(
    status: string
  ): string {


    switch (status) {


      case 'Pending':

        return 'pending';


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


  openAddMilestone(): void {


    this.editingMilestone =

      false;


    this.currentMilestone = {


      id: 0,


      name: '',


      description: '',


      plannedDate: '',


      actualDate: '',


      status: 'Pending'


    };


    this.showModal = true;

  }


  editMilestone(
    milestone: Milestone
  ): void {


    this.editingMilestone =

      true;


    this.currentMilestone = {

      ...milestone

    };


    this.showModal = true;

  }


  saveMilestone(): void {


    if (

      this.editingMilestone

    ) {


      const index =

        this.milestones.findIndex(

          milestone =>

            milestone.id ===

            this.currentMilestone.id

        );


      if (index !== -1) {


        this.milestones[index] =

          {

            ...this.currentMilestone

          };

      }


      alert(

        'Milestone updated successfully!'

      );


    } else {


      const newMilestone: Milestone = {


        ...this.currentMilestone,


        id:

          this.getNextId()

      };


      this.milestones.push(

        newMilestone

      );


      alert(

        'Milestone added successfully!'

      );

    }


    this.closeModal();

  }


  deleteMilestone(
    id: number
  ): void {


    const confirmed =

      confirm(

        'Are you sure you want to delete this milestone?'

      );


    if (!confirmed) {

      return;

    }


    this.milestones =

      this.milestones.filter(

        milestone =>

          milestone.id !== id

      );


    alert(

      'Milestone deleted successfully!'

    );

  }


  closeModal(): void {


    this.showModal =

      false;

  }


  private getNextId(): number {


    if (

      this.milestones.length === 0

    ) {

      return 1;

    }


    return Math.max(

      ...this.milestones.map(

        milestone =>

          milestone.id

      )

    ) + 1;

  }

}